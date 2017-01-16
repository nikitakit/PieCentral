from enum import Enum

class Commands(Enum):
  ESTOP = "0"
  START_GAME = "1"
  TELEOP = "2"
  END_GAME = "3"