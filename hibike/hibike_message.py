from __future__ import print_function
# Rewritten because Python.__version__ != 3
import serial
import struct
import pdb
import os
import json

config_file = open(os.path.join(os.path.dirname(__file__), 'hibikeDevices.json'), 'r')
devices = json.load(config_file)
devices = {device["id"]: device for device in devices}

"""
structure of devices
{0: 
    {"id": 0, "name": "LimitSwitch", "params": [
                                               {"number": 0, "name": "switch0", "type": "bool", "read": True, "write": False}
                                               ]
    }
}

"""

# Dictionary mapping param types to python struct format characters
paramTypes = {
  "bool" : "?",
  "uint8_t": "B",
  "int8_t": "b", 
  "uint16_t": "H",
  "int16_t": "h", 
  "uint32_t": "I",
  "int32_t": "i", 
  "uint64_t": "Q",
  "int64_t": "q", 
  "float": "f",
  "double": "d"
}

# Dictionary of message types: message id
messageTypes = {
  "Ping" :                 0x10,
  "SubscriptionRequest" :  0x11,
  "SubscriptionResponse" : 0x12,
  "DeviceRead" :           0x13,
  "DeviceWrite" :          0x14,
  "DeviceData" :           0x15,
  "Error" :                0xFF
}

# Dictionary of device types: enumeration
deviceTypes = {
  "LimitSwitch"   :       0x00,
  "LineFollower"  :       0x01,
  "Potentiometer" :       0x02,
  "Encoder"       :       0x03,
  "BatteryBuzzer" :       0x04,
  "TeamFlag"      :       0x05,
  "Grizzly"       :       0x06,
  "ServoControl"  :       0x07,
  "LinearActuator":       0x08,
  "ColorSensor"   :       0x09,
  "DistanceSensor":       0x10,
  "MetalDetector" :       0x11,
  "ExampleDevice" :       0xFFFF
}

# Dictionary of error names : error codes
errorCodes = {
  "UnexpectedDelimiter" : 0xFD,
  "CheckumError"        : 0xFE,
  "GenericError"        : 0xFF
}

class HibikeMessage:
  def __init__(self, messageID, payload):
    assert messageID in messageTypes.values()
    self._messageID = messageID
    self._payload = payload[:]
    self._length = len(payload)

  def getmessageID(self):
    return self._messageID

  # Returns a copy of payload as a bytearray
  def getPayload(self):
    return self._payload[:]

  def toByte(self):
    m_buff = bytearray()
    m_buff.append(self._messageID)
    m_buff.append(self._length)
    m_buff.extend(self.getPayload())
    return m_buff

  def __str__(self):
    return str([self._messageID] + [self._length] + list(self._payload))

  def __repr__(self):
    return str(self)




# return the top 16 bits of UID
def getDeviceType(uid):
  return int(uid >> 72)

# return bits [71: 64] of the UID
def getYear(uid):
  temp = uid >> 64
  return int(temp & 0xFF)

# return bits[63: 0] of the UID
def getID(uid):
  return uid & 0xFFFFFFFFFFFFFFFF


# Given a message, computes the checksum
def checksum(data):
  # Remove this later after development
  assert type(data) == bytearray, "data must be a bytearray"

  chk = data[0]
  for i in range(1, len(data)):
    chk ^= data[i]
  return chk

# Sends this message
# Computes the checksum
# Then sends each byte of the message, and finally sends the checksum byte
def send(serial_conn, message):
  m_buff = message.toByte()
  chk = checksum(m_buff)
  m_buff.append(chk)
  encoded = cobs_encode(m_buff)
  out_buf = bytearray([0x00, len(encoded)]) + encoded
  serial_conn.write(out_buf)



def make_ping():
  """ Makes and returns Ping message."""
  payload = bytearray()
  message = HibikeMessage(messageTypes["Ping"], payload)
  return message

def make_subscription_request(device_id, params, delay):
  """ Makes and returns SubscriptionRequest message.

      looks up config data about the specified 
      device_id to properly construct the message.
      
      device_id - a device type id (not uid).
      params    - an iterable of param names
      delay     - the delay in milliseconds
  """
  raise NotImplementedError()

def make_subscription_response(device_id, params, delay, uid):
  """ Makes and returns SubscriptionResponse message.

      looks up config data about the specified 
      device_id to properly construct the message.
      
      device_id - a device type id (not uid).
      params    - an iterable of param names
      delay     - the delay in milliseconds
      uid       - the uid
  """
  raise NotImplementedError()

def make_device_read(device_id, params):
  """ Makes and returns DeviceRead message.

      looks up config data about the specified 
      device_id to properly construct the message.
      
      device_id - a device type id (not uid).
      params    - an iterable of param names
  """
  raise NotImplementedError()

def make_device_write(device_id, params_and_values):
  """ Makes and returns DeviceWrite message.
      If all the params cannot fit, it will fill as many as it can.

      looks up config data about the specified 
      device_id to properly construct the message.
      
      device_id         - a device type id (not uid).
      params_and_values - an iterable of param (name, value) tuples
  """
  raise NotImplementedError()

def make_device_data(device_id, params_and_values):
  """ Makes and returns SubscriptionRequest message.
      If all the params cannot fit, it will fill as many as it can.

      looks up config data about the specified 
      device_id to properly construct the message.
      
      device_id         - a device type id (not uid).
      params_and_values - an iterable of param (name, value) tuples
  """
  raise NotImplementedError()

def make_error(error_code):
  """ Makes and returns Error message."""
  temp_payload = struct.pack('<B', error_code)
  payload = bytearray(temp_payload)
  message = HibikeMessage(messageTypes["Error"], payload)
  return message

# constructs a new object Message by continually reading from input
# Uses dictionary to figure out length of data to know how many bytes to read
# Returns:
    # None if no message
    # -1 if checksum does not match
    # Otherwise returns a new HibikeMessage with message contents
def read(serial_conn):
  
  # deal with cobs encoding
  while serial_conn.inWaiting() > 0:
    if struct.unpack('<B', serial_conn.read())[0] == 0:
      break
  else:
    return None
  message_size = struct.unpack('<B', serial_conn.read())[0]
  encoded_message = serial_conn.read(message_size)
  message = cobs_decode(encoded_message)
  

  if len(message) < 2:
    return None
  messageID, payloadLength = struct.unpack('<BB', message[:2])
  if len(message) < 2 + payloadLength + 1:
    return None
  payload = message[2:2 + payloadLength]

  chk = struct.unpack('<B', message[2+payloadLength:2+payloadLength+1])[0]
  if chk != checksum(message[:-1]):
    print(chk, checksum(message[:-1]), list(message))
    return -1

  return HibikeMessage(messageID, payload)

# cobs helper functions
def cobs_encode(data):
  output = bytearray()
  curr_block = bytearray()
  for byte in data:
    if byte:
      curr_block.append(byte)
      if len(curr_block) == 254:
        output.append(1 + len(curr_block))
        output.extend(curr_block)
        curr_block = bytearray()
    else:
      output.append(1 + len(curr_block))
      output.extend(curr_block)
      curr_block = bytearray()
  output.append(1 + len(curr_block))
  output.extend(curr_block)
  return output

def cobs_decode(data):
  output = bytearray()
  index = 0
  while (index < len(data)):
    block_size = data[index] - 1
    index += 1
    if index + block_size > len(data):
      return bytearray()
    output.extend(data[index:index + block_size])
    index += block_size
    if block_size + 1 < 255 and index < len(data):
      output.append(0)
  return output
