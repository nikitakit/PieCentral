import time, random
import threading
import multiprocessing
import hibike_message as hm
import queue
import glob
import serial
__all__ = ["hibike_process"]

fake_uids = [0 << 72, 7 << 72]


uid_to_index = {}
#port_to_index = {}

def hibike_process(badThingsQueue, stateQueue, pipeFromChild):
    while pipeFromChild.recv()[0] != "ready":
        pass
    ports = []#['0', '1']
    serials = [int(port) for port in ports]




    # each device has it's own write thread, with it's own instruction queue
    instruction_queues = [queue.Queue() for _ in ports]


    # since this is a simulation and there are no real devices, this is how the write threads interface with the read threads
    fake_device_queues = [queue.Queue() for _ in ports]

    # each device has one write thread that receives instructions from the main thread and writes to devices
    write_threads = [FakeDeviceWriteThread(ser, iq, fake_device_queue) for ser, iq, fake_device_queue in zip(serials, instruction_queues, fake_device_queues)]
    
    # each device has a read thread that reads from devices and writes directly to stateManager
    read_threads = [FakeDeviceReadThread(ser, None, stateQueue, fake_device_queue) for ser, fake_device_queue in zip(serials, fake_device_queues)]
    

    real_ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
    real_serials = [serial.Serial(port, 115200) for port in real_ports]
    real_instruction_queues = [queue.Queue() for _ in real_ports]
    real_write_threads = [RealDeviceWriteThread(ser, iq) for ser, iq in zip(real_serials, real_instruction_queues)]
    real_read_threads = [RealDeviceReadThread(index + len(ports), ser, None, stateQueue) for index, ser in enumerate(real_serials)]

    ports += real_ports
    serials += real_serials
    instruction_queues += real_instruction_queues
    write_threads += real_write_threads
    read_threads += real_read_threads

    print(ports)

    for read_thread in read_threads:
        read_thread.start()
    for write_thread in write_threads:
        write_thread.start()

    # the main thread reads instructions from statemanager and forwards them to the appropriate device write threads
    while True:
        instruction, args = pipeFromChild.recv()
        if instruction == "enumerate_all":
            for instruction_queue in instruction_queues:
                instruction_queue.put(("ping", []))
        elif instruction == "subscribe_device":
            uid = args[0]
            if uid in uid_to_index:
                instruction_queues[uid_to_index[uid]].put(("subscribe", args))
        elif instruction == "write_params":
            uid = args[0]
            if uid in uid_to_index:
                instruction_queues[uid_to_index[uid]].put(("write", args))            


class RealDeviceWriteThread(threading.Thread):

    def __init__(self, ser, instructionQueue):
        self.ser = ser
        self.queue = instructionQueue
        super().__init__()

    def run(self):
        while True:
            instruction, args = self.queue.get()

            if instruction == "ping":
                hm.send(self.ser, hm.make_ping())
            elif instruction == "subscribe":
                print(args)
                uid = args[0]
                delay = args[1]
                params = args[2]
                hm.send(self.ser, hm.make_subscription_request(hm.uid_to_device_id(uid), params, delay))
            elif instruction == "write":
                uid = args[0]
                params_and_values = args[1]
                hm.send(self.ser, hm.make_device_write(hm.uid_to_device_id(uid), params_and_values))
            # self.fake_device_queue.put(instruction)

class FakeDeviceWriteThread(threading.Thread):

    def __init__(self, ser, instructionQueue, fake_device_queue):
        self.ser = ser
        self.queue = instructionQueue
        self.fake_device_queue = fake_device_queue
        super().__init__()

    def run(self):
        while True:
            instruction = self.queue.get()
            self.fake_device_queue.put(instruction)

class RealDeviceReadThread(threading.Thread):

    def __init__(self, index, ser, errorQueue, stateQueue):
        self.index = index
        self.ser = ser
        self.errorQueue = errorQueue
        self.stateQueue = stateQueue
        self.delay = 0
        self.params = []
        self.uid = None

        super().__init__()

    def run(self):
        while True:
            packet = hm.blocking_read(self.ser)
            message_type = packet.getmessageID()
            if message_type == hm.messageTypes["SubscriptionResponse"]:
                params, delay, uid = hm.parse_subscription_response(packet)
                self.uid = uid
                uid_to_index[uid] = self.index
                self.stateQueue.put(("device_subscribed", [uid, delay, params]))
            elif message_type == hm.messageTypes["DeviceData"]:
                if self.uid is not None:
                    params_and_values = hm.parse_device_data(packet, hm.uid_to_device_id(self.uid))
                    self.stateQueue.put(("device_values", params_and_values))
                else:
                    print("[HIBIKE] Port %s received data before enumerating!!!" % self.ser.port)

class FakeDeviceReadThread(threading.Thread):

    def __init__(self, ser, errorQueue, stateQueue, fake_device_queue):
        self.ser = ser
        self.errorQueue = errorQueue
        self.stateQueue = stateQueue
        self.fake_device_queue = fake_device_queue
        self.delay = 0
        self.params = []

        self.fake_subscription_thread = FakeSubscriptionThread(fake_uids[self.ser], 0, [], self.fake_device_queue)
        self.fake_subscription_thread.start()
        super().__init__()

    def run(self):
        while True:
            instruction, args = self.fake_device_queue.get()
            res = None
            if instruction == "ping":
                uid, delay, params = fake_uids[self.ser], self.delay, self.params
                uid_to_index[uid] = self.ser
                res = ["device_subscribed", [uid, delay, params]]
            elif instruction == "subscribe":
                uid, delay, params = tuple(args)
                uid_to_index[uid] = self.ser
                res = ["device_subscribed", [uid, delay, params]]

                self.fake_subscription_thread.quit = True
                self.fake_subscription_thread.join()
                self.fake_subscription_thread = FakeSubscriptionThread(uid, delay, params, self.fake_device_queue)
                self.fake_subscription_thread.start()
            elif instruction == "device_values":
                res = [instruction, args]

            self.stateQueue.put(res)





            # instruction, args = self.fake_device_queue.get()
            # res = None
            # if instruction == "ping":
            #     uid, delay, params = fake_uids[self.ser], self.delay, self.params
            #     uid_to_index[uid] = self.ser
            #     res = ["device_subscribed", [uid, delay, params]]
            # elif instruction == "subscribe":
            #     uid, delay, params = tuple(args)
            #     uid_to_index[uid] = self.ser
            #     res = ["device_subscribed", [uid, delay, params]]

            #     self.fake_subscription_thread.quit = True
            #     self.fake_subscription_thread.join()
            #     self.fake_subscription_thread = FakeSubscriptionThread(uid, delay, params, self.fake_device_queue)
            #     self.fake_subscription_thread.start()
            # elif instruction == "device_values":
            #     res = [instruction, args]

            # self.stateQueue.put(res)

class FakeSubscriptionThread(threading.Thread):

    def __init__(self, uid, delay, params, fake_device_queue):
        self.uid = uid
        self.delay = delay
        self.params = params
        self.fake_device_queue = fake_device_queue
        self.quit = False
        super().__init__()

    def run(self):
        if self.delay != 0:
            while True:
                if self.quit:
                    return
                time.sleep(self.delay / 1000.0)
                param_types = [hm.paramMap[hm.uid_to_device_id(self.uid)][param][1] for param in self.params]
                params_and_values = {}
                for param, param_type in zip(self.params, param_types):
                    if param_type in ("bool", ):
                        params_and_values[param] = random.choice([True, False])
                    elif param_type in ("uint8_t", "int8_t", "uint16_t", "int16_t", "uint32_t", "int32_t", "uint64_t", "int64_t"):
                        params_and_values[param] = random.randrange(256)
                    else:
                        params_and_values[param] = random.random()
                self.fake_device_queue.put(("device_values", [self.uid, list(params_and_values.items())]))


#############
## TESTING ##
#############

if __name__ == "__main__":

    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def set_sequence_interval(functions, sec):
        def func_wrapper():
            set_sequence_interval(functions[1:] + functions[:1], sec)
            functions[0]()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def make_send_write(pipeToChild, uid, params_and_values):
        def helper():
            pipeToChild.send(["write_params", [uid, params_and_values]])
        return helper



    pipeToChild, pipeFromChild = multiprocessing.Pipe()
    badThingsQueue = multiprocessing.Queue()
    stateQueue = multiprocessing.Queue()
    newProcess = multiprocessing.Process(target=hibike_process, name="hibike_sim", args=[badThingsQueue, stateQueue, pipeFromChild])
    newProcess.daemon = True
    newProcess.start()
    pipeToChild.send(["ready", []])
    pipeToChild.send(["enumerate_all", []])
    uids = set()
    while True:
        command, args = stateQueue.get()
        if command == "device_subscribed":
            uid = args[0]
            if uid not in uids:
                uids.add(uid)
                if hm.devices[hm.uid_to_device_id(uid)]["name"] == "TeamFlag":
                    set_sequence_interval([
                        make_send_write(pipeToChild, uid, [("led1", 1), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 1), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 1), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 1), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 1)]), 
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 1), ("yellow", 0)])
                        ], 0.1)
                pipeToChild.send(["subscribe_device", [uid, 10, [param["name"] for param in hm.devices[hm.uid_to_device_id(uid)]["params"]]]])
        elif command == "device_values":
            print("%10.2f, %s" % (time.time(), str(args)))
    # print(stateQueue.get())
    # print(stateQueue.get())
    # print(stateQueue.get())
    # pipeToChild.send(["subscribe_device", [0, 1000, ["switch0", "switch2"]]])
    # print(stateQueue.get())
    # while True:
    #     print(stateQueue.get())
