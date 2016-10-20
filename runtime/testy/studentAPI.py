from runtimeUtil import *

class Robot:
  def __init__(self, toManager, fromManager):
    self.fromManager = fromManager
    self.toManager = toManager

  def createKey(self, key, *args):
    """ Creates a new key, or nested keys if more than 1 key is passed in.
        If any nested key does not exist, it will be created.
    """
    self.__commandHelper(SM_COMMANDS.CREATE_KEY, [[key] + list(args)])

  def getValue(self, key, *args):
    """Returns the value associated with key
    """
    return self.__commandHelper(SM_COMMANDS.GET_VAL, [[key] + list(args)])

  def setValue(self, value, key, *args):
    """Sets the value associated with key
    """
    #statemanager passes exception, then check to see if returned value is exception or not
    self.__commandHelper(SM_COMMANDS.SET_VAL, [value, [key] + list(args)])

  def __commandHelper(self, command, args_list):
    self.toManager.put([command, args_list], PROCESS_NAMES.STUDENT_CODE)
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIError):
      raise message
    return message
