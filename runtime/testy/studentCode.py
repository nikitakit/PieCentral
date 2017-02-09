import time
from runtimeUtil import *

def setup():
  pass

def main():
  pass

def asyncawait_setup():
  Robot.createKey("right")
  Robot.createKey("counter")
  Robot.setValue(3.0, "right") 
  Robot.setValue(0.0, "counter")
  Robot.run(asyncawait_helper)

def asyncawait_main():
  Robot.setValue(Robot.getValue("counter") + 1, "counter")
  if Robot.getValue("right") == 4 and Robot.getValue("counter") == 3:
    print("Async Success")

async def asyncawait_helper():
  '''Robot.createKey("left")
  Robot.setValue(1.0, "left")
  curr = time.time()
  await Actions.sleep(2.0)
  now = time.time()
  if now - curr > 1.5:
    if now - curr < 2.5:
      print("Success")
  Robot.setValue(0.0, "left")
  if Robot.getValue("left") != 0.0:
    print("Value Set Error")'''
  Robot.setValue(Robot.getValue("right") + 1, "right")

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

  Robot.setValue(response, "incrementer")

  print("Saying hello to the other side")
  print("DAT:", 1.0/response)

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

def createKey_setup():
  Robot.createKey("Restarts")
  Robot.setValue(0, "Restarts")
  if Robot.getValue("Restarts") != 0:
    print("Either getValue or setValue is not working correctly")
  pass

def createKey_main():
  Robot.createKey("Restarts")
  if Robot.getValue("Restarts") == 0:
    try:
      print("Making sure setValue can't create new key")
      Robot.setValue(707, "Klefki")
    except StudentAPIKeyError:
      print("Success!")
    else:
      print("ERROR: setValue can create keys :(")

  print("Creating key 'Klefki' and setting to value 707")
  Robot.createKey("Klefki")
  Robot.setValue(707, "Klefki")
  print("Success!")

  print("Creating nested keys")
  Robot.createKey("Mankey", "EVOLUTION")
  Robot.setValue("Primeape", "Mankey", "EVOLUTION")
  print("Success!")
  restarts = Robot.getValue("Restarts")
  Robot.setValue(restarts+1, "Restarts")

def hibikeSubscribeDevice_setup():
  pass

def hibikeSubscribeDevice_main():
  Robot._hibikeSubscribeDevice(1, 2, [3, 4])
  time.sleep(.01) # Wait for command to propogate to Hibike
  print(Robot.getValue("hibike", "device_subscribed"))

def timestamp_setup():
  pass

def timestamp_main():
  path = ["dict1", "inner_dict_1_string"]

  print("Getting timestamp")
  initialTime = Robot.getTimestamp(*path)
  print("Success!")

  print("Setting timestamp")
  Robot.setValue("bye", *path)
  print("Success!")

  print("Getting new timestamp")
  newTime = Robot.getTimestamp(*path)
  if newTime > initialTime and time.time() - newTime < 1:
    print("Success!")
  else:
    print("Timestamp did not update correctly")

  print("Testing nested timestamps")
  if newTime == Robot.getTimestamp(*path[:-1]):
    print("Success!")
  else:
    print("Nested timestamps did not update correctly")

def infiniteSetupLoop_setup():
  print("setup")
  while True:
    time.sleep(.1)

def infiniteSetupLoop_main():
  print("main")

def infiniteMainLoop_setup():
  print("setup")

def infiniteMainLoop_main():
  print("main")
  while True:
    time.sleep(.1)

def emergencyStop_setup():
  print("E-Stop setup")


def emergencyStop_main():
  response = Robot.getValue("incrementer")
  response -= 1
  if(response < 0):
    Robot.emergencyStop()

  Robot.setValue(response, "incrementer")
  print("HIBIKE LOOP")

def hibikeSensorMappings_setup():
  pass

def hibikeSensorMappings_main():
  print(Robot._hibikeGetUID('zero'))
  print(Robot._hibikeGetUID('one'))
  print(Robot._hibikeGetUID('two'))
  print(Robot._hibikeGetUID('three'))
