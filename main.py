import socket
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

while True:
    if (machine_config.get_myturn() == False):
        data, addr = sock.recvfrom(1024)
        print("received message:")
        print(data.decode(), addr)
        machine_config.set_myturn(True)
    else:
        msg = input("input: ")
        print("sending " + msg + " to:")
        print (machine_config.get_next()["ip"], machine_config.get_next()["port"])
        sock.sendto(msg.encode(), (machine_config.get_next()["ip"], machine_config.get_next()["port"]))
        machine_config.set_myturn(False)
