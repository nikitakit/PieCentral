import hibike_process
from multiprocessing import Process, Pipe, Queue
from enum import Enum, unique

class Hibike:

    def __init__(self):

        self.badThingsQueue = Queue()
        self.stateQueue     = Queue()
        self.pipeTochild, self.pipeFromChild = Pipe()
        self.hibike_process = Process(target=hibike_process.hibike_process, args=(badThingsQueue, stateQueue, pipeFromChild))
        self.hibike_process.daemon = True
        self.hibike_process.start()

    def ready(self):
        self.pipeTochild.send(["ready"])

    def enumerate(self):
        self.pipeTochild.send(["enumerate_all"])

    def subscribe(self, uid, delay, params):
        self.pipeTochild.send(["subscribe", uid, delay, params])

    def write(self, uid, params_and_values):
        self.pipeTochild.send(["write", uid, params_and_values])

    def read(self, uid, params):
        self.pipeTochild.send(["read", uid, params])

if __name__ = '__main__':
    h = Hibike()
    h.ready()
    h.enumerate()
    while True:
        print(h.stateQueue.get())
