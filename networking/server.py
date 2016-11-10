import socket

HOST = 'localhost'
PORT = 3141

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(5)
    while 1:
        conn, addr = s.accept()
        msg = bytes()
        rec = conn.recv(1024)
        while rec != bytes():
            msg += rec
            rec = conn.recv(1024)
        print(msg.decode('UTF8'))
