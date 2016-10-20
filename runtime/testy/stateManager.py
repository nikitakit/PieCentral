import sys

from runtimeUtil import *

# TODO:
# 0. modify self.state to acually store (name, value) pairs
class StateManager(object):

  """input is a multiprocessing.Queue object to support multiple
  processes requesting state data
  """
  def __init__(self, badThingsQueue, inputQueue, runtimePipe):
    self.initRobotState()
    self.badThingsQueue = badThingsQueue
    self.input = inputQueue
    self.commandMapping = self.makeCommandMap()
    # map process names to pipes
    self.hibikeMapping = self.makeHibikeMap()
    self.processMapping = {PROCESS_NAMES.RUNTIME: runtimePipe}

  def makeCommandMap(self):
    commandMapping = {
      SM_COMMANDS.RESET : self.initRobotState,
      SM_COMMANDS.ADD : self.addPipe,
      SM_COMMANDS.GET_VAL : self.getValue,
      SM_COMMANDS.SET_VAL : self.setValue,
      SM_COMMANDS.STUDENT_MAIN_OK : self.studentCodeTick,
      SM_COMMANDS.CREATE_KEY : self.createKey
    }
    return commandMapping

  def makeHibikeMap(self):
    hibikeMapping = {
      HIBIKE_COMMANDS.ENUMERATE: self.hibikeEnumerateAll,
      HIBIKE_COMMANDS.SUBSCRIBE: self.hibikeSubscribeDevice,
      HIBIKE_COMMANDS.READ: self.hibikeReadParams,
      HIBIKE_COMMANDS.WRITE: self.hibikeWriteParams
    }
    return hibikeMapping

  def initRobotState(self, callingProcess=None):
    self.state = {
     "incrementer" : 2,
     "int1" : 112314,
     "float1": 987.123,
     "bool1" : True,
     "dict1" : {"inner_dict1_int" : 555, "inner_dict_1_string": "hello"},
     "list1" : [70, "five", 14.3],
     "string1" : "abcde",
     "runtime_meta" : {"studentCode_main_count" : 0}
    }

  def addPipe(self, callingProcess, processName, pipe):
    self.processMapping[processName] = pipe
    pipe.send(RUNTIME_CONFIG.PIPE_READY.value)

  def createKey(self, callingProcess, keys):
    currDict = self.state
    for key in keys:
      try:
        if key not in currDict:
          currDict[key] = {}
        currDict = currDict[key]
      except TypeError:
        error = StudentAPIKeyError(
          "key '{}' is defined, but does not contain a dictionary.".format(key))
        self.processMapping[callingProcess].send(error)
        return
    self.processMapping[callingProcess].send(None)

  def getValue(self, callingProcess, keys):
    result = self.state
    try:
      for key in enumerate(keys):
        i = key[0]
        result = result[key[1]]
      self.processMapping[callingProcess].send(result)
    except:
      error = StudentAPIKeyError(self.dictErrorMessage(i, keys, result))
      self.processMapping[callingProcess].send(error)

  def setValue(self, callingProcess, value, keys):
    currDict = self.state
    i = 0
    try:
      for key in enumerate(keys[:-1]):
        i = key[0]
        currDict = currDict[key[1]]
      if len(keys) > 1:
        i += 1
      if keys[i] not in currDict:
        raise Exception
      currDict[keys[i]] = value
      self.processMapping[callingProcess].send(value)
    except:
      error = StudentAPIKeyError(self.dictErrorMessage(i, keys, currDict))
      self.processMapping[callingProcess].send(error)

  def studentCodeTick(self, callingProcess):
    self.state["runtime_meta"]["studentCode_main_count"] += 1

  def hibikeEnumerateAll(self, pipe):
    pipe.send([HIBIKE_COMMANDS.ENUMERATE.value])

  def hibikeSubscribeDevice(self, pipe, uid, delay, params):
    pipe.send([HIBIKE_COMMANDS.SUBSCRIBE.value, uid, delay, params])

  def hibikeWriteParams(self, pipe, uid, param_values):
    pipe.send([HIBIKE_COMMANDS.WRITE.value, uid, param_values])

  def hibikeReadParams(self, pipe, uid, params):
    pipe.send([HIBIKE_COMMANDS.READ.value, uid, params])

  def dictErrorMessage(self, erroredIndex, keys, currDict):
    keyChain = ""
    i = 0
    while (i < erroredIndex):
      # Assembles a string representation of the dictionary indexing that occurred
      keyChain += "['" + keys[i] + "']" if (type(keys[i]) is str) else "[" + str(keys[i]) + "]"
      i += 1
    keys = [None] if len(keys) == 0 else keys
    erroredKey = "'" + keys[erroredIndex] + "'" if type(keys[erroredIndex]) is str else str(keys[erroredIndex])
    errorMessage = "KeyError: key " + erroredKey + " not found in state" + keyChain + "\n"

    if type(currDict) is dict:
      # Converts all available keys to strings, and adds commas and spaces at the end of each element
      availableKeys = [("'" + el + "', " if type(el) is str else str(el) + ", ") for el in currDict.keys()]
      if len(availableKeys) > 0:
        # Removes comma and space from last item in availableKeys
        availableKeys[-1] = availableKeys[-1][:-2]
      errorMessage += "Available keys in state" + keyChain + ": " + "".join(availableKeys)
    else:
      errorMessage += "state" + keyChain + " is of type " + type(currDict).__name__

    return errorMessage

  def start(self):
    # TODO: Make sure request is a list/tuple before attempting to access
    # And that there are the correct number of elements
    while True:
      request = self.input.get(block=True)

      listSize = 3

      if(len(request) != listSize):
        self.badThingsQueue.put(BadThing(sys.exc_info(), "Wrong input size, need list of size {0}, got size {1}".format(listSize, len(request)), event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))

      cmdType = request[0]
      processName = request[1]
      args = request[2]

      if(cmdType not in self.commandMapping):
        self.badThingsQueue.put(BadThing(sys.exc_info(), "Unknown process name: %s" % (request,), event = BAD_EVENTS.UNKNOWN_PROCESS, printStackTrace = False))
      else:
        command = self.commandMapping[cmdType]
        command(processName, *args)
