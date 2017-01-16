import lcm
import threading
import time
from config import Commands as cmd

def heartbeat_handler(channel, data):
  """
  Prints out heartbeat data
  """
  data = data.decode()
  msg = data.split(' ')
  print("Robot {}: state {}".format(msg[0], msg[1]))
  
lc = lcm.LCM()
subscription = lc.subscribe("ROBOT_HEARTBEAT", heartbeat_handler)

def teleop():
  lc.publish("COMMANDS", cmd.TELEOP.value)

def start_game():
  lc.publish("COMMANDS", cmd.START_GAME.value)

def end_game():
  lc.publish("COMMANDS", cmd.END_GAME.value)

def estop():
  """
  Sends out estop command. Will repeat until interrupted
  """
  try:
    while True:
      lc.publish("COMMANDS", cmd.ESTOP.value)
  except KeyboardInterrupt:
    pass

def heartbeat_listen(lc, robot_number):
  """
  Subthread intended to listen for heartbeats
  """
  while True:
    lc.handle()
    
t = threading.Thread(target = heartbeat_listen, args = (lc, 1))
t.daemon=True
t.start()