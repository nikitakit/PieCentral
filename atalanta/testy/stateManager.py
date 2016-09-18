# import multiprocessing
import sys

from runtimeUtil import *

class StateManager(object):

  """input is a multiprocessing.Queue object to support multiple
  processes requesting state data
  """
  def __init__(self, badThingsQueue, inputQueue, runtimePipe):
    self.initRobotState()
    self.badThingsQueue = badThingsQueue
    self.input = inputQueue
    # map process names to pipes
    self.processMapping = {PROCESS_NAMES.RUNTIME: runtimePipe}

  def initRobotState(self):
    self.state = {} #{1L: ['val', 'type']} actual mapping
    self.nameMap = {'name':'UID'}
    self.gamepadData = []

  def addPipe(self, processName, pipe):
    self.processMapping[processName] = pipe
    pipe.send(SM_COMMANDS.READY)

  def start(self):
    while True:
      request = self.input.get(block=True)

      if request[0] == SM_COMMANDS.RESET:
        self.initRobotState()

      elif request[0] == SM_COMMANDS.ADD:
        self.addPipe(request[1], request[2])

      elif request[0] == SM_COMMANDS.HELLO:
        self.state[0] -= 1
        self.processMapping[PROCESS_NAMES.STUDENT_CODE].send(self.state[0])
      elif (request[0] == SM_COMMANDS.SEND):
        sendPipe = self.processMapping[PROCESS_NAMES.ANSIBLE_PACKAGER]
        sendPipe.send(self.state)
      elif (request[0] == SM_COMMANDS.STORE):
        self.gamepadData = request[1]
      else:
        self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (request,), event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))
