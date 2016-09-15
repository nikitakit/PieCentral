import time
from runtimeUtil import *

def setup(pipe):
  pipe.recv()
  # startupValue = 5
  # print("Setting Up State = %d" % (startupValue,))
  # state[0] = startupValue

<<<<<<< HEAD
def main(state):
  print("Hello from the other side %d" % (state[0],))
  #1.0/state[0]
  state[0] -= 1
=======
def main(stateQueue, pipe):
  print("Saying hello to the other side")
  stateQueue.put([SM_COMMANDS.HELLO])
  state = pipe.recv()
  print("Hello from the other side %d" % (state,))
  1.0/state
>>>>>>> devel_yizhe
