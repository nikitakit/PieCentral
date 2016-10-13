from runtimeUtil import *


class Robot:
    def __init__(self, toManager, fromManager):
        self.fromManager = fromManager
        self.toManager = toManager
        # Wait for ack from SM before continuing
        self.fromManager.recv()

    def getValue(self, key):
        """Returns the value associated with key
    """
<<<<<<< HEAD
        # TODO: Actually use key
        self.toManager.put([SM_COMMANDS.GET_VAL, [key]])
        return self.fromManager.recv()
=======
    self.toManager.put([SM_COMMANDS.GET_VAL, [[key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message
>>>>>>> 811f95983336b3df3b93fe4ffaf865731679e34b

    def setValue(self, key, value):
        """Sets the value associated with key
    """
<<<<<<< HEAD
        # TODO: Implement
        self.toManager.put([SM_COMMANDS.SET_VAL, [key, value]])
        return self.fromManager.recv()
=======
    #statemanager passes exception, then check to see if returned value is exception or not
    self.toManager.put([SM_COMMANDS.SET_VAL, [value, [key] + list(args)]])
    message = self.fromManager.recv()
    if isinstance(message, StudentAPIKeyError):
        raise message
    return message
>>>>>>> 811f95983336b3df3b93fe4ffaf865731679e34b
