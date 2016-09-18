import socket
import threading
import queue
import time
import runtime_proto_pb2
import fake_dawn
import random
import ansible_pb2
import sys
from runtimeUtil import *
data = [0] #for testing purposes
sendPort = 1235
recvPort = 1236
tcp_port = 1237
stateToEnum = {0:runtime_proto_pb2.RuntimeData.STUDENT_CRASHED,
        1:runtime_proto_pb2.RuntimeData.STUDENT_RUNNING,
        2:runtime_proto_pb2.RuntimeData.STUDENT_STOPPED,
        3:runtime_proto_pb2.RuntimeData.TELEOP,
        4:runtime_proto_pb2.RuntimeData.AUTO
        }
#Custom buffer for handling states. Holds two states, updates one and sends the other.
class two_buffer(): 
    def __init__(self):
        self.data = [0, 0]
        self.put_index = 0
        self.get_index = 1
    def replace(self, item):
        self.data[self.put_index] = item
        self.put_index = (self.put_index + 1) % 2
        self.get_index = (self.get_index + 1) % 2
    def get(self):
        return self.data[self.get_index]

sendBuffer = two_buffer()
recvBuffer = two_buffer()
raw_fake_data = [[0]]
packed_fake_data = [[0]]
dawn_buffer = [0]
###Protobuf handlers###
#Function for handling unpackaging of protobufs from Dawn
def unpackage(data):
    dawnData = ansible_pb2.DawnData()
    try:
        dawn_data.ParseFromString(data)#Change from bytes to actual data
        return dawn_data
    except:#if it's a None class, TODO: handle this here instead sending a message that no data is coming from dawn
        return data
#Handles packaging and sending state to dawn in the form of protobuf we define
def package(state, badThingsQueue):
    proto_message = runtime_proto_pb2.RuntimeData()
    try:
        for devId, devVal in state.items(): #Parse through entire state and package it
            if(devID is 'studentCodeState'):
                proto_message.robot_state = stateToEnum[devVal] #check if we are dealing with sensor data or student code state
            else:
                test_sensor = proto_message.sensor_data.add() #Create new submessage for each sensor and add corresponding values
                test_sensor.device_name = devId
                test_sensor.device_type = devVal[0]
                test_sensor.value = state[1]
        return bytes(proto_message.SerializeToString()) #return the serialized data as bytes to be sent to Dawn
    except Exception:
        badThingsQueue.put(BadThing(sys.exc_info(), None))
###Start Ansible Thread Chain###
def packageData(badThingsQueue, stateQueue, pipe):
    while(True):
        try:
            rawState = pipe.recv() #Pull state from the pipe
            if (rawState == SM_COMMANDS.READY):
                stateQueue.put([SM_COMMANDS.SEND, 1])
            elif(rawState):
                packState = package(rawState, badThingsQueue)
                sendBuffer.replace(pack_state) ##Used list mutation as it's an atomic operation
        except Exception:
            badThingsQueue.put(BadThing(sys.exc_info(), None))

def udpSender(badThingsQueue, stateQueue, pipe):
    host = socket.gethostname()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:#DGRAM for UDP sockets
        while(True): #constantly send the state to Dawn
            try:
                msg = sendBuffer.get()
                if(msg != 0):
                    s.sendto(msg, (host, sendPort))
            except Exception:
                badThingsQueue.put(BadThing(sys.exc_info(), None))
def udpReceiver(badThingsQueue, stateQueue, pipe):
    #same thing as the client side from python docs
    host = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #DGRAM for UDP sockets
    s.bind((host, recvPort))
    while(True):
        try:
            data = s.recv(2048)
            recvBuffer.replace(data)
        except Exception: 
            badThingsQueue.put(BadThing(sys.exc_info(), None))
def unpackageData(badThingsQueue, stateQueue, pipe):
    ready = False;
    while(True):
        try:
            ready = pipe.recv()
            if(ready):
                unpackagedData = unpackage(recvBuffer.get())
                stateQueue.put([SM_COMMANDS.STORE, unpackagedData])
        except Exception:
            badThingsQueue.put(BadThing(sys.exc_info(), None))
def tcpSender(port, sendQueue, badThingsQueue, stateQueue, ):
    try:
        host = socket.gethostname()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while(True):
                    try:
                        conn.sendall(sendQueue.get(block=True))
                    except QueueEmpty:
                        pass
    except Exception:
        badThingsQueue.put(BadThing(sys.exc_info(),None))
def tcpReceiver(port, recvQueue, badThingsQueue):
    try:
        host = socket.gethostname()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            while(True):
                recvData = s.recv(2048)
                recvQueue.put(recvData)
    except Exception:
        badThingsQueue.put(BadThing(sys.exc_info(), None))




        


    




  


