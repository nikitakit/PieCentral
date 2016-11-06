import socket

s = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

s.connect(('localhost', 3141))

msg = raw_input('message: ')
while msg != '':
    sent = s.send(msg)
    msg = msg[sent:]
s.shutdown(socket.SHUT_RDWR)
s.close()