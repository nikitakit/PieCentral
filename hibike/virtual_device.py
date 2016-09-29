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
subResponseTime = 0

while True:
	msg = hm.read(conn)
	if not msg:
                if ((delay != 0) && (subResponseTime != 0) && ((time.time() - subResponseTime) % delay == 0)#If it's time to send a data update, do what's below
                    if (device_type == 00x0) # If the device type is a limit switch, send 4 booleans via a data update
                        statusVars = struct.pack("<????", (true, false, false, true))
                        dataUpdate = HibikeMessage(0x02, statusVars)
                        hm.send(conn, dataUpdate)
                    if 
		time.sleep(.001)
		continue
	if msg.getmessageID() in (hm.messageTypes["SubscriptionRequest"],
                delay = struct.unpack("<H")
                hm.send(conn, hm.make_sub_response(device_type, year, id, delay))
                subResponseTime = time.time()
        if msg.getmessageID()in (hm.messageTypes["Ping"]):
		hm.send(conn, hm.make_sub_response(device_type, year, id, delay))
        if 
        
