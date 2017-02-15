#!/usr/bin/python3
import time
from multiprocessing import Process, Manager, Value, Pipe, Queue

iter_count = int(1e5)

def client(queue, pipe, name=''):
    for _ in range(iter_count):
        queue.put("signal")
        value = pipe.recv()
        queue.put(value+1)

def server(queue, pipe, name=''):
    value = {0: {0: {0: 0}}}
    while True:
        queue.get()
        pipe.send(value[0][0][0])
        value[0][0][0] = queue.get()

if __name__ == "__main__":
    q = Queue()
    p1, p2 = Pipe()
    s = Process(target=server, args=(q, p1))
    s.start()

    c = Process(target=client, args=(q, p2))
    start_time = time.time()
    c.start()
    c.join()
    end_time = time.time()

    print("{0:.3f}".format(end_time - start_time))
    s.terminate()
