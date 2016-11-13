import time, random
import threading
import multiprocessing
import hibike_message as hm
import queue

__all__ = ["hibike_process"]

fake_uids = [0 << 72, 7 << 72]


uid_to_index = {}


def hibike_process(badThingsQueue, stateQueue, pipeFromChild):
    ports = ['0', '1']
    serials = [int(port) for port in ports]

    # each device has it's own write thread, with it's own instruction queue
    instruction_queues = [queue.Queue() for _ in ports]

    # since this is a simulation and there are no real devices, this is how the write threads interface with the read threads
    fake_device_queues = [queue.Queue() for _ in ports]

    # each device has one write thread that receives instructions from the main thread and writes to devices
    write_threads = [threading.Thread(target=runDeviceWrite, args=(ser, iq, fake_device_queue), daemon=True) for ser, iq, fake_device_queue in zip(serials, instruction_queues, fake_device_queues)]
    
    # each device has a read thread that reads from devices and writes directly to stateManager
    read_threads = [threading.Thread(target=runDeviceRead, args=(ser, None, stateQueue, fake_device_queue), daemon=True) for ser, fake_device_queue in zip(serials, fake_device_queues)]
    
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
                print("putting onto instruction_queue: " + str(args))
                instruction_queues[uid_to_index[uid]].put(("subscribe", args))
            else:
                print('not found uid')

def runDeviceWrite(ser, instructionQueue, fake_device_queue):
    while True:
        print("deviceWrite waiting")
        instruction = instructionQueue.get()
        fake_device_queue.put(instruction)
        print("deviceWrite done waiting, put: " + str(instruction))

def runDeviceRead(ser, errorQueue, stateQueue, fake_device_queue):
    delay = 0
    params = []

    thread_ready = threading.Event()
    stop_event = threading.Event()
    fake_subscription_thread = threading.Thread(target=runFakeSubscription, args=(fake_uids[ser], 0, [], fake_device_queue, thread_ready, stop_event), daemon=True)
    fake_subscription_thread.start()
    thread_ready.wait()
    thread_ready.clear()

    while True:
        print("deviceRead waiting")
        instruction, args = fake_device_queue.get()
        print("deviceRead got: " + str(instruction) + " : " + str(args))
        res = None
        if instruction == "ping":
            uid, delay, params = fake_uids[ser], delay, params
            uid_to_index[uid] = ser
            res = ["device_enumerated", [uid, delay, params]]
        elif instruction == "subscribe":
            uid, delay, params = tuple(args)
            uid_to_index[uid] = ser
            res = ["device_subscribed", [uid, delay, params]]

            print("setting stop_event")
            stop_event.set()
            fake_subscription_thread.join()
            print("thread alive: " + str(fake_subscription_thread.is_alive()))
            stop_event.clear()
            print("clearing stop_event")
            fake_subscription_thread = threading.Thread(target=runFakeSubscription(uid, delay, params, fake_device_queue, thread_ready, stop_event), daemon=True)
            fake_subscription_thread.start()
            thread_ready.wait()
            thread_ready.clear()
            print("started new thread")
        elif instruction == "device_values":
            res = [instruction, args]

        print("printing\n" + str(res) + "\n\n")
        stateQueue.put(res)

def runFakeSubscription(uid, delay, params, fake_device_queue, thread_ready, stop_event):
    thread_ready.set()
    if delay != 0:
        print("delay: " + str(delay))
        while True:
            if stop_event.is_set():
                print("stop_event: " + str(stop_event.is_set()))
                return
            print("stop_event False, delay: " + str(delay))
            time.sleep(delay / 1000.0)
            param_types = [hm.paramMap[hm.uid_to_device_id(uid)][param][1] for param in params]
            params_and_values = {}
            for param, param_type in zip(params, param_types):
                if param_type in ("bool", ):
                    params_and_values[param] = random.choice([True, False])
                elif param_type in ("uint8_t", "int8_t", "uint16_t", "int16_t", "uint32_t", "int32_t", "uint64_t", "int64_t"):
                    params_and_values[param] = random.randrange(256)
                else:
                    params_and_values[param] = random.random()
            fake_device_queue.put(("device_values", [uid, list(params_and_values.items())]))
    else:
        print("delay was 0")


#############
## TESTING ##
#############

if __name__ == "__main__":
    pipeToChild, pipeFromChild = multiprocessing.Pipe()
    badThingsQueue = multiprocessing.Queue()
    stateQueue = multiprocessing.Queue()
    newProcess = multiprocessing.Process(target=hibike_process, name="hibike_sim", args=[badThingsQueue, stateQueue, pipeFromChild])
    newProcess.daemon = True
    newProcess.start()
    pipeToChild.send(["enumerate_all", []])
    print(stateQueue.get())
    print(stateQueue.get())
    print("sending pipeToChild")
    pipeToChild.send(["subscribe_device", [0, 1000, ["switch0", "switch2"]]])
    print("done sending pipe"   )
    print(stateQueue.get())
    while True:
        print(stateQueue.get())
