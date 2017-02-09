import csv

from runtimeUtil import *

class Actions:
  async def sleep(seconds):
    await asyncio.sleep(seconds)

class StudentAPIObject:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager

  def _getSMValue(self, key, *args):
    """Returns the value associated with key
    """
    self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  def _setSMValue(self, value, key, *args):
    """Sets the value associated with key
    """
    #statemanager returns value, then method checks to see whether exception
    self.toManager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

class Gamepad(StudentAPIObject):
  def get_value(name):
    return self._getSMValue('dawn', 0, name) #assumes gamepad by default at 0

  def get_value(name, gamepad_number):
    return self._getSMValue('dawn', gamepad_number, name)

class Robot(StudentAPIObject):
  def __init__(self, toManager, fromManager):
    StudentAPIObject.__init__(self, toManager, fromManager)
    self._createSensorMapping()

  def get_value(self, device_name):
    uid = _hibikeGetUID(device_name)
    return self._getSMValue('hibike', uid)

  def set_value(self, device_name, value):
    uid = _hibikeGetUID(device_name)
    # TODO: verify that this correctly sends values to Hibike
    self.toManager.put([HIBIKE_COMMANDS.SET_VAL, [uid, value]]) #should list be nested?
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message

  def disable(self, device_name):
    uid = _hibikeGetUID(device_name)
    self.toManager.put([HIBIKE_COMMANDS.DISABLE, [uid]]) #should list be nested?
    message = self.fromManager.recv()
    if isinstance(message, StudentAPITypeError):
        raise message
    return message

  def set_coast(self, device_name, coast_enabled):
    pass

  def is_running(coro):
    pass

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
        raise StudentAPIKeyError()

  def emergencyStop(self):
    self.toManager.put([SM_COMMANDS.EMERGENCY_STOP, []])
