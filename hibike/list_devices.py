import glob
import serial
import hibike_message as hm
import struct
ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
print(ports)

serials = [serial.Serial(port, 115200) for port in ports]
devices = []
for s in serials:
	hm.send(s, hm.make_ping())

while serials:
	remaining = []
	for s in serials:
		reading = hm.read(s)
		if reading:
			params, delay, device_type, year, uid = struct.unpack("<HHHBQ", reading.getPayload())
			devices.append(hm.device_id_to_name(device_type))
		else:
			remaining.append(s)
	serials = remaining
print(devices)
	
