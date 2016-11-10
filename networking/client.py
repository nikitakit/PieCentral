import socket

PORT = 3141
HOST = 'localhost'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    msg = bytes(input('message: '), 'UTF8')
    s.sendall(msg)

