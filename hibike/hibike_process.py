import threading
import multiprocessing

class WriteThread(threading.Thread):

	def __init__(self, instructionQueue):
		self.queue = instructionQueue

	def run(self):
		while True:
			instruction = self.queue.get()
			print instruction

class ReadThread(threading.Thread):

	def __init__(self, serialPort, errorQueue, stateQueue):
		self.serialPort = serialPort
		self.errorQueue = errorQueue
		self.stateQueue = stateQueue
		while True:
			# try to read a packet from serial port
			# if an exception is caught (device disconnect) send it to errorQueue
			# if a packet is read and the serial port has enumerated a uid, send the packet to stateQueue
			pass
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																											
def hibike_process(badThingsQueue, stateQueue, pipeFromChild):

	# spawn a read thread for each serial port
	# span a write thread
	# tell the write thread to ping each serial port
	# read things off from pipeFromChild