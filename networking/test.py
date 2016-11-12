import subprocess
import time
import filecmp
import sys

infilename = "test.py"

outfile = open("testout.txt", "w")
infile = open(infilename, 'r')
server = subprocess.Popen(["python3", "server.py"], stdout = outfile)
time.sleep(1)
client = subprocess.Popen(["python3", "client.py", "-p"], stdin = infile, stdout = subprocess.DEVNULL)
time.sleep(3)
server.terminate()
time.sleep(1)
subprocess.call("sed -i '$ d' testout.txt", shell=True) #recieved file has newline at end
print(filecmp.cmp("testout.txt", infilename))

