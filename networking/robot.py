import lcm
import threading
import time
from config import Commands as cmd

class Robot():
  """
  Basic robot simulator. Features
  game states as well as estop and basic i/o
  """
  def __init__(self, number):
    self.number = number
    self.teleop = False
    self.motors = [0]*4
    self.sensors = [True, 4]
    self.enabled = False
    self.estop = False
        
def heartbeat(lc, number):
  """
  Generates heartbeats for the robot
  sends robot number as well as state flag
  (0 = disabled, 1 = autonomous, 2 = teleop, 3 = estop)
  """
  i = 0
  while True:
    i += 1
    state = robot.enabled + robot.teleop + robot.estop*2
    status = "{} {}".format(robot.number, state)
    lc.publish("ROBOT_HEARTBEAT", status)
    time.sleep(5)
        
def cmd_handler(channel, data):
  """
  Handles recieved commands
  """
  data = cmd(data)
  if data == cmd.ESTOP:
    robot.enabled = False
    robot.estop = True

  if data == cmd.START_GAME:
    robot.enabled = True

  if data == cmd.TELEOP:
    robot.teleop = True
    
  if data == cmd.END_GAME:
    robot.enabled = False
    
lc = lcm.LCM()
subscription = lc.subscribe("COMMANDS", cmd_handler)

robot = Robot(1)

t = threading.Thread(target = heartbeat, args = (lc, robot))
t.daemon=True
t.start()

try:
  while True:
      lc.handle()
except KeyboardInterrupt:
    pass
