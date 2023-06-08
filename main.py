import socket
import netifaces as ni

class Config:
    def __init__(self, numplayers, config, index, ip):
        self.numplayers = numplayers
        self.config = config
        self.index = index
        self.ip = ip

    def get_port(self):
        return int(self.config[self.index][2])
    
    def get_next(self):
        if (self.index < self.numplayers - 1):
            return self.config[self.index + 1]
        return self.config[0]


ip = ni.ifaddresses('wlp2s0')[ni.AF_INET][0]['addr']

config_file = open("config.txt", "r")
config = []
for i, line in enumerate(config_file):
    if (i == 0):
        numplayers = line.split(":")[1][:-1]
        continue
    cfgline = line.split(" ")
    addr = cfgline[1].split(":")[1]
    port = cfgline[2].split(":")[1][:-1]
    config.append((i, addr, port))
    if addr == ip:
        myindex = i-1

machine_config = Config(int(numplayers), config, myindex, ip)
print(machine_config.get_next())

config_file.close()

UDP_IP = machine_config.ip
UDP_PORT = machine_config.get_port()
MESSAGE = b"Hello, World!"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((machine_config.ip, machine_config.get_port()))

# while True:
#     data, addr = sock.recvfrom(1024)
#     print("received message from: %s: %s" % addr % data)
#     sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
