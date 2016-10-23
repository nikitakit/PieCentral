import threading
import multiprocessing
import hibike_message as hm

port_to_uid = {}
uid_to_port {}
serials = {}

class RuntimeReadThread(threading.Thread):

    def __init__(self, pipeFromChild):
        self.runtime_pipe = pipeFromChild

    def run(self):
        while True:
            instruction = self.runtime_pipe.recv()
            print(instruction)

class DeviceWriteThread(threading.Thread):

    def __init__(self, instructionQueue):
        self.queue = instructionQueue

    def run(self):
        while True:
            instruction = self.queue.get()
            print(instruction)

class DeviceReadThread(threading.Thread):

    def __init__(self, ser, errorQueue, stateQueue):
        self.ser = ser
        self.errorQueue = errorQueue
        self.stateQueue = stateQueue

    def run(self):
        while True:
            message = hm.blocking_read(self.ser)
            print(message.getPayload())

            if message.getmessageID() == hm.messageTypes["SubscriptionResponse"]:
                params, delay, device_type, year, id = struct.unpack("<HHHBQ", message.getPayload())
                uid = (device_type << 72) | (year << 64) | id
                port_to_uid[self.ser.port] = uid
                print("got a subscription")

            elif message.getmessageID() == hm.messageTypes["DeviceData"]:
            	print("got some data")

            # try to read a packet from serial port
            # if an exception is caught (device disconnect) send it to errorQueue
            # if a packet is read and the serial port has enumerated a uid, send the packet to stateQueue
            pass
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
def hibike_process(badThingsQueue, stateQueue, pipeFromChild):

    while True:
        instruction = pipeFromChild.recv()
        if instruction[0] == "enumerate_all":
            stateQueue.put(["device_subscribed", 0, 0, []])

    # spawn a read thread for each serial port
    # span a write thread
    # tell the write thread to ping each serial port
    # read things off from pipeFromChild