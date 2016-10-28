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

device_id = hm.deviceTypes[device]
year = 1
id = random.randint(0, 0xFFFFFFFFFFFFFFFF)
delay = 0
updateTime = 0
uid = (device_id << 72) | (year << 64) | id

# Here, the parameters and values to be sent in device datas are set for each device type and the parameter subscription status is set to false for all params
if device_type in [hm.deviceTypes["LimitSwitch"]]: 
        param_subscriptions = [False, False, False, False]
        params_and_values = [(hm.devices["switch0", True), ("switch1", True), ("switch2", False), ("switch3", False)]
if device_type in [hm.deviceTypes["ServoControl"]]:
        param_subscriptions = [False, False, False, False, False, False, False]
        params_and_values = [(0, 2), (1, True), (2, 0), (3, True), (4, 5), (5, True), (6, 3), (7, False)]

while (True):
        if (updateTime != 0 and delay != 0):
                if((time.time() - updateTime) >= (delay * 0.001)): #If the time equal to the delay has elapsed since the previous device data, send a device data with the device id and the device's params and values                                            
 
                        device_data = hm.make_device_data(device_id, params_and_values)
                        hm.send(conn, dataUpdate)
                        updateTime = time.time()

             
        msg = hm.read(conn)
        if not msg:
             time.sleep(.001)
             continue
        if msg.getmessageID() in [hm.messageTypes["SubscriptionRequest"]]: #Update the delay, subscription time, and params, then send a subscription response 
             params, delay = struct.unpack("<HH", msg.getPayload())
             hm.send(conn, hm.make_sub_response(device_id, params, delay, uid))
             
             subscribed_params = hm.decode_params(device_id, params)
             for sub_status in param_subscriptions:
                if sub_status in subscribed_params:
                   sub_status = True
                else
                   sub_status = False
                
             updateTime = time.time()
        if msg.getmessageID() in [hm.messageTypes["Ping"]]: # Send a subscription response 
             hm.send(conn, hm.make_sub_response(device_id, params, delay, uid))
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

