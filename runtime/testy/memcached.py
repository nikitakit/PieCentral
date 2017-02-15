#!/usr/bin/python3.5
import time
from multiprocessing import Process, Manager, Value, Pipe
import pylibmc

iter_count = int(1e5)

def client(mc, name=''):
    for _ in range(iter_count):
        mc[bytes(1)][0][0][0] = mc[bytes(1)][0][0][0]+1

def server(mc, name=''):
    mc[bytes(1)] = {0: {0: {0: 0}}}

if __name__ == "__main__":
    mc = pylibmc.Client(["127.0.0.1"], binary=True,
            behaviors={"tcp_nodelay": True,
                            "ketama": True})

    s = Process(target=server, args=(mc,))
    s.start()
    s.join()

    c = Process(target=client, args=(mc,))
    start_time = time.time()
    c.start()
    c.join()
    end_time = time.time()

    print("{0:.3f}".format(end_time - start_time))
    s.terminate()
