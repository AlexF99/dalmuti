import socket
import time
from config import Config

machine_config = Config(socket.gethostbyname(socket.gethostname()))
print("num players: " + str(machine_config.numplayers))
print("i am on:")
print(machine_config.get_local())
print("next:")
print(machine_config.get_next())
print("my port is:" + str(machine_config.get_port()))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((machine_config.ip, machine_config.get_port()))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

while True:
    if (machine_config.get_myturn() == False):
        data, addr = sock.recvfrom(1024)
        print("received message from: %s: %s" % addr % data)
    else:
        msg = input("input: ")
        print("sending " + msg + " to:")
        print (machine_config.get_next()["ip"], machine_config.get_next()["port"])
        sock.sendto(msg.encode(), (machine_config.get_next()["ip"], machine_config.get_next()["port"]))
