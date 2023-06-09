import socket
from config import Config
import random

deck = []
for i in range(1, 13):
    for j in range(i):
        deck.append(i)

random.shuffle(deck)
print(deck)

machine_config = Config(socket.gethostbyname(socket.gethostname()))
print("num players: " + str(machine_config.numplayers))
print("i am on:")
print(machine_config.get_local())
print("next:")
print(machine_config.get_next())
print("my port is:" + str(machine_config.get_port()))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((machine_config.ip, machine_config.get_port()))

# shuffling & dealing
if machine_config.main:
    input("press anything to start shuffling: ")
    deck = []
    for i in range(1, 13):
        for j in range(i):
            deck.append(i)

    random.shuffle(deck)
    for i, card in enumerate(deck):
        if i == machine_config.index:
            machine_config.receive_card(card)
        else:
            print("player %d gets card %d" % (i % machine_config.numplayers, card))
            sock.sendto(str(card).encode(), (machine_config.get_next()["ip"], machine_config.get_next()["port"]))

    for i in range(machine_config.numplayers):
        if i != machine_config.index:
            sock.sendto("endshuffle".encode(), (machine_config.get_next()["ip"], machine_config.get_next()["port"]))
else:
    data, addr = sock.recvfrom(1024)
    while (data.decode() != "endshuffle"):
        print("received message:")
        received = data.decode()
        print(received)
        machine_config.receive_card(received)
        data, addr = sock.recvfrom(1024)

# playing
while True:
    if (machine_config.myturn == False):
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
