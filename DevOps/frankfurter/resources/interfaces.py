import paramiko
from scp import SCPClient


f = open('interfaces', 'r')
a = []
for line in f:
    a.append(line)
f.close()

# a[3] = 'test\n'
f = open('interfaces', 'w')
for line in a:
    f.write(line)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.7.2', username='ubuntu', password='temppwd')

scp = SCPClient(ssh.get_transport())

scp.put('./interfaces', '/ect/network/')
ssh.close()
