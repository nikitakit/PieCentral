"""
   This library contains a set of functions that allow the user to manually send and recieve  messages to and from a device by calling functions
"""

import hibike_message as hm
import hibike_process as hp
import multiprocessing


class HibikeCommunicator:
   def _init_():
       """ 
          Set up the pipes for communication between the device and the Beegle Bum Black, creates a thread to recieve communications from the device, and starts up the process that runs the communication
       """
       
       # This block creates the pipes
       self.pipeToChild, pipeFromChild = multiprocessing.Pipe()
       
       # This block creates the process
       badThingsQueue = multiprocessing.Queue()
       self.stateQueue = multiprocessing.Queue()
       newProcess = multiprocessing.Process(target=hp.hibike_process, name="hibike_sim", args=[badThingsQueue,self.stateQueue, pipeFromChild])
       newProcess.daemon = True
       newProcess.start()
       self.pipeToChild.send(["enumerate_all", []])

       # This block creates the thread
       threading.Thread(target = print_output)
   
   def print_ouput():
   """
      Prints out messages from the devices that are uploaded by newProcess to stateQueue
   """
      try:
         output = self.stateQueue.get_nowait()
      except QueueEmpty:
         continue
      print(output)

   def write(uid, params_and_values):
       """
          Sends a Device Write to a device

          uid - the device's uid
          params_and_values - an iterable of param (name, value) tuples
       """
       self.pipeToChild.send(["write_params", [uid, params_and_values]])
   
    def read(uid, params): 
        """
           Sends a Device Read to a device
        
           uid - the device's uid
           params - an iterable of the names of the params to be read
        """
        self.pipeToChild.send(["read_params", [uid, params]])
        
    def subscribe(uid, delay, params):
        """
           Subscribes to the device
           
           uid - the device's uid
           delay - the delay between device datas to be sent
           params - an iterable of the names of the params to be subscribed to
        """
        self.pipeToChild.send(["read_params", [uid, delay, params]])
