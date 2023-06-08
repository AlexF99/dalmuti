import socket
import time
from config import Config

machine_config = Config(socket.gethostbyname(socket.gethostname()))
print(machine_config.get_local())
print(machine_config.get_next())
print("my port is:" + str(machine_config.get_port()))

UDP_IP = machine_config.ip
UDP_PORT = machine_config.get_port()
MESSAGE = b"Hello, World!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((machine_config.ip, machine_config.get_port()))

while True:
    if (machine_config.get_ismain() == False):
        data, addr = sock.recvfrom(1024)
        print("received message from: %s: %s" % addr % data)
    else:
        time.sleep(1)
        sock.sendto(MESSAGE, (machine_config.get_next()[1], machine_config.get_next()[2]))
