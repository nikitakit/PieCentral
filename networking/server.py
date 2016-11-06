import socket

s = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

s.bind(('localhost', 3141))
s.listen(5)
while 1:
    (cs, addr) = s.accept()
    msg = ''
    rec = cs.recv(1024)
    while rec:
        msg += rec
        rec = cs.recv(1024)
    print(msg)