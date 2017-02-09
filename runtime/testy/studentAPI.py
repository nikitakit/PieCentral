import csv

from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager
    self._createSensorMapping()
    self.savedValues = {}

  def _createSensorMapping(self, filename = 'namedPeripherals.csv'):
    self.sensorMappings = {}
    with open(filename, 'r') as f:
        sensorMappings = csv.reader(f)
        for name, uid in sensorMappings:
            self.sensorMappings[name] = int(uid)

  def createKey(self, key, *args):
    """ Creates a new key, or nested keys if more than 1 key is passed in.
        If any nested key does not exist, it will be created.
    """
    self.toManager.put([SM_COMMANDS.CREATE_KEY, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return

  def getValue(self, key, *args):
    """Returns the value associated with key
    """
    self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  def setValue(self, value, key, *args):
    """Sets the value associated with key
    """
    #statemanager passes exception, then check to see if returned value is exception or not
    self.toManager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  def getTimestamp(self, key, *args):
    """Returns the value associated with key
    """
    self.toManager.put([SM_COMMANDS.GET_TIME, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  # TODO: Only for testing. Remove in final version
  def _hibikeSubscribeDevice(self, uid, delay, params):
    """Uses direct uid to access hibike."""
    self.toManager.put([HIBIKE_COMMANDS.SUBSCRIBE, [uid, delay, params]])

  def _hibikeGetUID(self, name):
    if name in self.sensorMappings:
        return self.sensorMappings[name]
    else:
        return None

  def emergencyStop(self):
    self.toManager.put([SM_COMMANDS.EMERGENCY_STOP, []])

  def sharedGetValue(self, key, *args):
    # Uses sharedMemory to boost performance
    # mutliprocessing.Value and multiprocessing.Array
    try:
        value, timestamp = self.keySearch(key, *args)

        if time.time() - timestamp.value  > STALE_DATA_TIMEOUT:
            raise KeyError # treat as if we never knew of this value

        return value.value

    except KeyError:
        self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])

        message = self.fromManager.recv()
        if isinstance(message, StudentAPIKeyError):
            raise message

        value = message
        self.toManager.put([SM_COMMANDS.GET_TIME, [[key] + list(args)]])
        timestamp = self.fromManager.recv()

        allKeys = [key] + list(args)
        currDict = self.savedValues
        for k in allKeys[:-1]:
            currDict = currDict[k]
        currDict[allKeys[-1]] = (value, timestamp)
        return value.value

  def keySearch(self, *args, fullPath=True):
    currValue = self.savedValues

    for key in args:
        currValue = currValue[key]

    if fullPath and isinstance(currValue, dict):     # Key path must be fully specified
        raise StudentAPIKeyError("Full key path not specified")

    return currValue # should be a (Value, Timestamp) tuple
