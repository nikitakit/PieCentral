import socket
import threading
import queue
import time
import runtime_pb2
import ansible_pb2
import notification_pb2

data = [0]
send_port = 1236
recv_port = 1235
tcp_port = 1234
dawn_hz = 10

def dawn_packager():
    proto_message = ansible_pb2.DawnData()
    proto_message.student_code_status = ansible_pb2.DawnData.TELEOP
    test_gamepad = proto_message.gamepads.add() 
    test_gamepad.index = 0
    test_gamepad.axes.append(.5)
    test_gamepad.buttons.append(True)
    return proto_message.SerializeToString()

def sender(port, send_queue):
    host = '127.0.0.1'
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            next_call = time.time()
            msg = dawn_packager()
            s.sendto(msg, (host, send_port))
            next_call += 1.0/dawn_hz
            time.sleep(max(next_call - time.time(), 0))

def receiver(port, receive_queue):
    host = '127.0.0.1'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, recv_port))
    while True:
        msg, addr = s.recvfrom(2048)
        runtime_message = runtime_pb2.RuntimeData()
        runtime_message.ParseFromString(msg)
        receive_queue[0]=msg

def tcp_relay(port):
    host = '127.0.0.1'
    msg = notification_pb2.Notification()
    msg.header = notification_pb2.Type.STUDENT_SENT
    msg = msg.SerializeToString()
    s  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    while True:
        next_call = time.time()
        s.send(msg)
        receive_msg, addr = s.recvfrom(2048)
        if receive_msg is None:
            continue
        else:
            msg = receive_msg
            parser = notification_pb2.Notification()
            parser.ParseFromString(receive_msg)
            print(parser.header)
        next_call += 1.0/dawn_hz
        time.sleep(max(next_call - time.time(), 0))


sender_thread = threading.Thread(target = sender, name = "fake dawn sender", args = (send_port, data))
recv_thread = threading.Thread(target = receiver, name = "fake dawn receiver", args = (recv_port, data))
sender_thread.daemon = True
recv_thread.daemon = True
recv_thread.start()
sender_thread.start()
tcp_thread = 
print("started threads")

#Just Here for testing, should not be run regularly
if __name__ == "__main__":
    while True:
    	time.sleep(1)
