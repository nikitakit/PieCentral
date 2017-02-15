#!/usr/bin/python3
import time
from multiprocessing import Process, Manager, Value, Pipe

iter_count = int(1e5)

def client(pipe, name=''):
    for _ in range(iter_count):
        pipe.send("signal")
        value = pipe.recv()
        pipe.send(value+1)

def server(pipe, name=''):
    value = {0: {0: {0: 0}}}
    while True:
        pipe.recv()
        pipe.send(value[0][0][0])
        value[0][0][0] = pipe.recv()

if __name__ == "__main__":
    con1, con2 = Pipe()
    s = Process(target=server, args=(con1,))
    s.start()

    c = Process(target=client, args=(con2,))
    start_time = time.time()
    c.start()
    c.join()
    end_time = time.time()

    print("{0:.3f}".format(end_time - start_time))
    s.terminate()
