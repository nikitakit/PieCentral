import time, random
import threading
import hibike_message as hm
import queue

fake_uids = [0 << 72, 7 << 72]


uid_to_index = {}


def hibike_process(badThingsQueue, stateQueue, pipeFromChild):
    while pipeFromChild.recv()[0] != "ready":
        pass
    rrt = RuntimeReadThread(pipeFromChild)
    ports = ['0', '1']
    serials = [int(port) for port in ports]
    instruction_queues = [queue.Queue() for _ in ports]
    fake_device_queues = [queue.Queue() for _ in ports]
    write_threads = [DeviceWriteThread(ser, iq, fake_device_queues) for ser, iq, fake_device_queue in zip(serials, instruction_queues, fake_device_queues)]
    read_threads = [DeviceReadThread(ser, errorQueue, stateQueue, fake_device_queue) for ser, fake_device_queue in zip(serials, fake_device_queues)]
    for read_thread in read_threads:
        read_thread.start()
    for write_thread in write_threads:
        write_thread.start()
    while True:
        instruction, args = pipeFromChild.recv()
        if instruction == "enumerate_all":
            for instruction_queue in instruction_queues:
                instruction_queue.put("ping", [])
        elif instruction == "subscribe_device":
            uid = args[0]
            if uid in uid_to_index:
                instruction_queues[uid_to_index[uid]].put("subscribe", args[1:])


        # if instruction[0] == "enumerate_all":
        #     stateQueue.put(["device_subscribed", 0, 0, []])

# class RuntimeReadThread(threading.Thread):

#     def __init__(self, ser, pipeFromChild):
#         self.runtime_pipe = pipeFromChild

#     def run(self):
#         while True:
#             instruction = self.runtime_pipe.recv()
#             print(instruction)

class DeviceWriteThread(threading.Thread):

    def __init__(self, ser, instructionQueue, fake_device_queue):
        self.ser = ser
        self.queue = instructionQueue
        self.fake_device_queue = fake_device_queue

    def run(self):
        while True:
            instruction = self.queue.get()
            fake_device_queue.put(instruction)

class DeviceReadThread(threading.Thread):

    def __init__(self, ser, errorQueue, stateQueue, fake_device_queue):
        self.ser = ser
        self.errorQueue = errorQueue
        self.stateQueue = stateQueue
        self.fake_device_queue = fake_device_queue
        self.delay = 0
        self.params = []

        self.fake_subscription_thread = FakeSubscriptionThread(fake_uids[self.ser], 0, [], self.fake_device_queue)
        self.fake_subscription_thread.start()

    def run(self):
        while True:
            instruction, args = self.fake_device_queue.get()
            res = None
            if instruction == "ping":
                uid, delay, params = fake_uids[self.ser], self.delay, self.params
                res = ["device_subscribed", [uid, delay, params]]
            elif instruction == "subscribe":
                uid, delay, params = tuple(args)
                res = ["device_subscribed", [uid, delay, params]]

                self.fake_subscription_thread.quit = True
                self.fake_subscription_thread.join()
                self.fake_subscription_thread = FakeSubscriptionThread(uid, delay, params, self.fake_device_queue)
                self.fake_subscription_thread.start()
            elif instruction == "device_values":
                res = [instruction, args]

            self.stateQueue.put(res)

            # message = hm.blocking_read(self.ser)
            # print(message.getPayload())

            # if message.getmessageID() == hm.messageTypes["SubscriptionResponse"]:
            #     params, delay, device_type, year, id = struct.unpack("<HHHBQ", message.getPayload())
            #     uid = (device_type << 72) | (year << 64) | id
            #     port_to_uid[self.ser.port] = uid
            #     print("got a subscription")

            # elif message.getmessageID() == hm.messageTypes["DeviceData"]:
            #     print("got some data")

            # try to read a packet from serial port
            # if an exception is caught (device disconnect) send it to errorQueue
            # if a packet is read and the serial port has enumerated a uid, send the packet to stateQueue

class FakeSubscriptionThread(threading.Thread):

    def __init__(self, uid, delay, params, fake_device_queue):
        self.uid = uid
        self.delay = delay
        self.params = params
        self.fake_device_queue = fake_device_queue
        self.quit = False

    def run(self):
        if self.delay != 0:
            while True:
                if self.quit:
                    return
                time.sleep(self.delay / 1000.0)
                param_types = [hm.paramMap[hm.uid_to_device_id(self.uid)][param]["type"] for param in self.params]
                params_and_values = {}
                for param, param_type in zip(self.params, param_types):
                    if param_type in ("bool", ):
                        params_and_values[param] = random.choice([True, False])
                    elif param_type in ("uint8_t", "int8_t", "uint16_t", "int16_t", "uint32_t", "int32_t", "uint64_t", "int64_t"):
                        params_and_values[param] = random.randrange(256)
                    else:
                        params_and_values[param] = random.random()
                self.fake_device_queue.put("device_values", [self.uid, list(params_and_values.items())])


#weight of each time interval for flipping.
#for example, there is a 5% chance the data will flip within 1 sec
cutoffs = [0.05, 0.13, 0.15, 0.27, 0.5, 0.73, 0.85, 0.95, 0.99, 1.0]

# Sensor type: (low value, high value, noise)
sensor_values = {
    '0x0000': (0, 1, 0),
    '0x0001': (200, 800, 100),
    '0x0002': (None, None, None),
    '0x0003': (-256, 256, 10),
    '0x0004': (0, 1, 0),
    '0x0005': (0, 1, 0),
    '0x0006': (None, None, None),
    '0x0007': (None, None, None),
    '0x0008': (None, None, None)
}

class Hibike:

    def __init__(self):
        self.UIDs = [
            '0x000000FFFFFFFFFFFFFFFF', '0x000100FFFFFFFFFFFFFFFF',
            '0x000200FFFFFFFFFFFFFFFF', '0x000300FFFFFFFFFFFFFFFF',
            '0x000400FFFFFFFFFFFFFFFF', '0x000500FFFFFFFFFFFFFFFF',
            '0x000600FFFFFFFFFFFFFFFF', '0x000700FFFFFFFFFFFFFFFF',
            '0x000800FFFFFFFFFFFFFFFF'
         ]
        #format Device Type (16) + Year (8) + ones (64)
        self.subscribedTo = {}
        self.sensors = []


    def getEnumeratedDevices(self):
        """ Returns a list of tuples of UIDs and device types. """

        enum_devices = []
        for UID in self.UIDs:
            enum_devices.append((UID, UID[:6])) # (UID - in hex, Device type - in hex)
        return enum_devices

    def subToDevices(self, deviceList):
        """ deviceList - List of tuples of UIDs and delays. Creates a dictionary
        storing UID, delay, time created (ms), previous data, whether data is
        low and flip times (the next time the data should flip). Flip is when
        data changes low to high or high to low.

        """

        for UID, delay in deviceList:
            if UID in self.UIDs and UID not in self.subscribedTo:
                last_time = time.time()*1000
                self.subscribedTo[UID] = {'delay': delay, 'time': last_time}
                self.subscribedTo[UID]['data'] = self.__getRandomData(UID, True)
                self.subscribedTo[UID]['is_low'] = True
                self.subscribedTo[UID]['flip_time'] = self.__calculateFlipTime(UID)
            elif UID in self.UIDs and  UID in self.subscribedTo:
                self.subscribedTo[UID]['delay'] = delay
        return 0

    def getData(self, UID, param):
        """ Extracts all data for specific UID. Checks whether to update data,
        flip data, or return previous data, and returns correct appropriate
        data.
        """

        #TODO: param is currently unused

        delay = self.subscribedTo[UID]['delay']
        last_time = self.subscribedTo[UID]['time']
        flip_time = self.subscribedTo[UID]['flip_time']
        curr_time = time.time()*1000

        should_flip = curr_time - delay >= flip_time
        should_update = curr_time - delay >= last_time

        if should_flip and should_update:
            self.subscribedTo[UID]['time'] = curr_time
            self.subscribedTo[UID]['data'] =  self.__getRandomData(UID, self.subscribedTo[UID]['is_low'])
            self.subscribedTo[UID]['flip_time'] = self.__calculateFlipTime(UID)
            self.subscribedTo[UID]['is_low'] = not self.subscribedTo[UID]['is_low']
        elif should_update:
            self.subscribedTo[UID]['time'] = curr_time
            self.subscribedTo[UID]['data'] = self.__getRandomData(UID, not self.subscribedTo[UID]['is_low'])
        return self.subscribedTo[UID]['data'] #returns sensor data

    def __calculateFlipTime(self, UID):
        """ Determines time of flip. """

        rand, last_time = random.random(), self.subscribedTo[UID]['time']
        noise = random.random()
        for i in range(len(cutoffs)):
            if rand < cutoffs[i]:
                return (time.time() + noise + i)*1000

    def __getRandomData(self, UID, is_low):
        """ Finds device_type of UID and returns corresponding flipped data."""

        device_type = UID[:6]
        low, high, noise = sensor_values[device_type]
        if low is None or high is None or noise is None:
            return 0 # TODO: what to do with these device types?
        if is_low:
            return high + (random.random() - .5) * noise
        else:
            return low + (random.random() - .5) * noise

############
## MOTORS ##
############

    def readValue(self, UID, param):
        #param values: 0 - delay, 1 - last_time, 2 - data
        try:
            return self.subscribedTo[UID][param]
        except:
            return 1

    def writeValue(self, UID, param, value):
        if param >= len(self.subscribedTo[UID]):
            return 1
        self.subscribedTo[UID][param] = value
        return 0


#############
## TESTING ##
#############

if __name__ == "__main__":
    hi = Hibike()
    hi.subToDevices([('0x000100FFFFFFFFFFFFFFFF', 1)])
