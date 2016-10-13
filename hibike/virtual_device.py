import struct
import serial
import hibike_message as hm
import sys
import random
import time
"""
This program should create a virtual hibike device for testing purposes

usage:
$ socat -d -d pty,raw,echo=0 pty,raw,echo=0
2016/09/20 21:29:03 socat[4165] N PTY is /dev/pts/26
2016/09/20 21:29:03 socat[4165] N PTY is /dev/pts/27
2016/09/20 21:29:03 socat[4165] N starting data transfer loop with FDs [3,3] and [5,5]
$ python3.5 virtual_device.py -d LimitSwitch -p /dev/pts/26
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--device', required=True, help='device type')
parser.add_argument('-p', '--port', required=True, help='serial port')
args = parser.parse_args()

device = args.device
port = args.port
print(device, port)
conn = serial.Serial(port, 115200)

device_type = hm.deviceTypes[device]
year = 1
id = random.randint(0, 0xFFFFFFFFFFFFFFFF)
delay = 0
updateTime = 0

while (True):
        if (updateTime != 0 and delay != 0):
                if((time.time() - updateTime) >= (delay * 0.001)): #If the time equal to the delay has elapsed since the previous data update, send a data update                                            
                        if device_type in [hm.deviceTypes["LimitSwitch"]]:  # If the device type is a limit switch, send 4 arbitrary booleans
                                statusVars = struct.pack("<????", True, False, False, True)
                        if device_type in [hm.deviceTypes["ServoControl"]]: # If the device is a servo control, send an empty packet
                                statusVars = struct.pack("<", ())

                        dataUpdate = hm.HibikeMessage(hm.messageTypes["DataUpdate"], statusVars)
                        hm.send(conn, dataUpdate)
                        updateTime = time.time()

             
        msg = hm.read(conn)
        if not msg:
             time.sleep(.001)
             continue
        if msg.getmessageID() in [hm.messageTypes["SubscriptionRequest"]]: #Update the delay and subscription time, and send a subscription response 
             delay = struct.unpack("<H", msg.getPayload())[0]
             hm.send(conn, hm.make_sub_response(device_type, year, id, delay))
             updateTime = time.time()
        if msg.getmessageID() in [hm.messageTypes["Ping"]]: # Send a subscription response 
             hm.send(conn, hm.make_sub_response(device_type, year, id, delay))
        if msg.getmessageID() in [hm.messageTypes["DeviceUpdate"]]: # Send a parameter and a value in a device response
             param, value = struct.unpack("<BI", msg.getPayload())
             responsePayload = struct.pack("<BI", param, value)
             deviceResponse = hm.HibikeMessage(hm.messageTypes["DeviceResponse"], responsePayload)
             hm.send(conn, deviceResponse)
        if msg.getmessageID() in [hm.messageTypes["DeviceStatus"]]:  # Send a parameter and a value in a device response  
             param = struct.unpack("<B", msg.getPayload())[0]
             value = 0
             responsePayload = struct.pack("<BI", param, value)
             deviceResponse = hm.HibikeMessage(hm.messageTypes["DeviceResponse"], responsePayload)
             hm.send(conn, deviceResponse)

