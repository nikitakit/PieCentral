import time, random
import threading
import multiprocessing
import hibike_message as hm
import queue
import glob
import serial
import os

__all__ = ["hibike_process"]


uid_to_index = {}
connect_write = True
uid_to_ser = {}

class Device:

    def __init__(self, ser, stateQueue):
        self.serial = ser
        self.instruction_queue = queue.Queue()
        self.write_thread = threading.Thread(target=device_write_thread, args=(ser, self.instruction_queue))
        self.read_thread = threading.Thread(target=device_read_thread, args=(ser, self.instruction_queue, None, stateQueue))
        self.uid

    def set_uid(self, uid):
        self.uid = uid


def hibike_process(badThingsQueue, stateQueue, pipeFromChild):

    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")

    try:
        virtual_device_config_file = os.path.join(os.path.dirname(__file__), "virtual_devices.txt")
        ports.extend(open(virtual_device_config_file, "r").read().split())
    except IOError:
        pass

    serials = [serial.Serial(port, 115200) for port in ports]

    devices = dict()

    for serial in serials:
        device = Device(serial, stateQueue)
        devices[serial] = device


    print(ports)

    for device in devices.values():
        device.read_thread.start()
        device.write_thread.start()    


    # the main thread reads instructions from statemanager and forwards them to the appropriate device write threads
    while True:
        instruction, args = pipeFromChild.recv()
        if instruction == "enumerate_all":
            for device in devices.values():
                device.instruction_queue.put(("ping", []))
        elif instruction == "subscribe_device":
            uid = args[0]
            if uid in uid_to_ser:
                devices[uid_to_ser[uid]].instruction_queue.put(("subscribe", args))
        elif instruction == "write_params":
            uid = args[0]
            if uid in uid_to_ser:
                devices[uid_to_ser[uid]].instruction_queue.put(("write", args))
        elif instruction == "read_params":
            uid = args[0]
            if uid in uid_to_ser:
                devices[uid_to_ser[uid]].instruction_queue.put(("read", args))

def device_write_thread(ser, queue):
    while True:
        instruction, args = queue.get()
        if instruction == "ping":
            hm.send(ser, hm.make_ping())
        elif instruction == "subscribe":
            uid, delay, params = args
            hm.send(ser, hm.make_subscription_request(hm.uid_to_device_id(uid), params, delay))
        elif instruction == "read":
            uid, params = args
            hm.send(ser, hm.make_device_read(hm.uid_to_device_id(uid), params))
        elif instruction == "write":
            uid, params_and_values = args
            hm.send(ser, hm.make_device_write(hm.uid_to_device_id(uid), params_and_values))
        elif instruction == "die":
            return



def device_read_thread(index, ser, instructionQueue, errorQueue, stateQueue):
    uid = None
    while True:
        try:
            packet = hm.blocking_read(ser)
            message_type = packet.getmessageID()
            if message_type == hm.messageTypes["SubscriptionResponse"]:
                params, delay, uid = hm.parse_subscription_response(packet)
                uid_to_ser[uid] = ser
                devices[ser].set_uid(uid)
                stateQueue.put(("device_subscribed", [uid, delay, params]))
            elif message_type == hm.messageTypes["DeviceData"]:
                if uid is not None:
                    params_and_values = hm.parse_device_data(packet, hm.uid_to_device_id(uid))
                    stateQueue.put(("device_values", params_and_values))
                else:
                    print("[HIBIKE] Port %s received data before enumerating!!!" % ser.port)
        except serial.serialutil.SerialException:
            stateQueue.put(("device_disconnected", [uid]))
            devices[ser].instruction_queue.put("die")
            del devices[ser]
            return


def enumerateSerialPorts(self):
    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")

#############
## TESTING ##
#############

if __name__ == "__main__":

    # helper functions so we can spawn threads that try to read/write to hibike_devices periodically
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
    pipeToChild.send(["enumerate_all", []])
    uids = set()
    while True:
        print("waiting for command")
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
                elif hm.devices[hm.uid_to_device_id(uid)]["name"] == "ServoControl":
                    set_interval_sequence([
                        make_send_write(pipeToChild, uid, [("servo0", 1), ("enable0", False), ("servo1", 21), ("enable1", True), ("servo2", 30), ("enable2", True), ("servo3", 8), ("enable3", True)]),
                        make_send_write(pipeToChild, uid, [("servo0", 5), ("enable0", False), ("servo1", 5), ("enable1", True), ("servo2", 5), ("enable2", True), ("servo3", 5), ("enable3", False)]),
                        make_send_write(pipeToChild, uid, [("servo0", 1), ("enable0", True), ("servo1", 26), ("enable1", True), ("servo2", 30), ("enable2", False), ("servo3", 17), ("enable3", True)]),
                        make_send_write(pipeToChild, uid, [("servo0", 13), ("enable0", False), ("servo1", 7), ("enable1", False), ("servo2", 24), ("enable2", True), ("servo3", 10), ("enable3", True)]),
                        make_send_write(pipeToChild, uid, [("servo0", 27), ("enable0", True), ("servo1", 2), ("enable1", False), ("servo2", 3), ("enable2", False), ("servo3", 14), ("enable3", False)]),
                        make_send_write(pipeToChild, uid, [("servo0", 20), ("enable0", True), ("servo1", 12), ("enable1", False), ("servo2", 20), ("enable2", False), ("servo3", 29), ("enable3", True)]),
                        ], 1)
                pipeToChild.send(["subscribe_device", [uid, 10, [param["name"] for param in hm.devices[hm.uid_to_device_id(uid)]["params"]]]])
        elif command == "device_values":
            print("%10.2f, %s" % (time.time(), str(args)))
