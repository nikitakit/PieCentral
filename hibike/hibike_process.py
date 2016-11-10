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

def hibike_process(badThingsQueue, stateQueue, pipeFromChild):

    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
    serials = [serial.Serial(port, 115200) for port in ports]

    # each device has it's own write thread, with it's own instruction queue
    instruction_queues = [queue.Queue() for _ in ports]

    # these threads receive instructions from the main thread and write to devices
    write_threads = [DeviceWriteThread(ser, iq) for ser, iq in zip(serials, instruction_queues)]

    # these threads receive packets from devices and write to statequeue
    read_threads = [DeviceReadThread(index, ser, iq, None, stateQueue) for index, (ser, iq) in enumerate(zip(serials, instruction_queues))]

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


class DeviceWriteThread(threading.Thread):

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
            elif instruction == "die":
                return


class DeviceReadThread(threading.Thread):

    def __init__(self, index, ser, instructionQueue, errorQueue, stateQueue):
        self.index = index
        self.ser = ser
        self.instructionQueue = instructionQueue
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


#############
## TESTING ##
#############

if __name__ == "__main__":

    # helper functions so we can spawn threads that try to
    def set_interval_sequence(functions, sec):
        def func_wrapper():
            set_interval_sequence(functions[1:] + functions[:1], sec)
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
                    set_interval_sequence([
                        make_send_write(pipeToChild, uid, [("led1", 1), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 1), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 1), ("led4", 0), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 1), ("blue", 0), ("yellow", 0)]),
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 0), ("yellow", 1)]), 
                        make_send_write(pipeToChild, uid, [("led1", 0), ("led2", 0), ("led3", 0), ("led4", 0), ("blue", 1), ("yellow", 0)])
                        ], 0.1)
                elif hm.devices[hm.uid_to_device_id(uid)]["name"] == "YogiBear":
                    set_interval_sequence([
                        make_send_write(pipeToChild, uid, [("duty", 0),   ("forward", True)]),
                        make_send_write(pipeToChild, uid, [("duty", 50),  ("forward", True)]),
                        make_send_write(pipeToChild, uid, [("duty", 100), ("forward", True)]),
                        make_send_write(pipeToChild, uid, [("duty", 0),   ("forward", False)]),
                        make_send_write(pipeToChild, uid, [("duty", 50),  ("forward", False)]),
                        make_send_write(pipeToChild, uid, [("duty", 100), ("forward", False)])
                        ], 1)
                pipeToChild.send(["subscribe_device", [uid, 10, [param["name"] for param in hm.devices[hm.uid_to_device_id(uid)]["params"]]]])
        elif command == "device_values":
            print("%10.2f, %s" % (time.time(), str(args)))
