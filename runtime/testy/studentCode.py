import time
from runtimeUtil import *

<<<<<<< HEAD

def setup(pipe):
    pass
    # startupValue = 5
    # print("Setting Up State = %d" % (startupValue,))
    # state[0] = startupValue

=======
def test0_setup():
  print("test0_setup")

def test0_main():
  print("test0_main")

def mainTest_setup():
  pass

def mainTest_main():
  response = Robot.getValue("incrementer")
  print("Get Info:", response)
  response -= 1
>>>>>>> 811f95983336b3df3b93fe4ffaf865731679e34b

def main(stateQueue, pipe):
    response = Robot.getValue("incrementer")
    print("Get Info:", response)
    response -= 1

    Robot.setValue("incrementer", response)

<<<<<<< HEAD
    print("Saying hello to the other side")
    print("DAT:", 1.0 / response)
=======
def nestedDict_setup():
  pass

def nestedDict_main():
  print("CODE LOOP")

  response = Robot.getValue("dict1", "inner_dict1_int")
  print("Get Info:", response)

  response = 1
  Robot.setValue(response, "dict1", "inner_dict1_int")
  response = Robot.getValue("dict1", "inner_dict1_int")
  print("Get Info2:", response)

def studentCodeMainCount_setup():
  pass

def studentCodeMainCount_main():
  print(Robot.getValue("runtime_meta", "studentCode_main_count"))
>>>>>>> 811f95983336b3df3b93fe4ffaf865731679e34b
