import socket
from player import Player
from network import Network
import random

network = Network()
network.init()

address = socket.gethostbyname(socket.gethostname())
player = network.get_chair(address)

# player = Player(socket.gethostbyname(socket.gethostname()))
print("num players: " + str(network.num_players))
print("i am on:")
print(player.get_local())
print("next:")
print(player.get_next())
print("my port is: " + str(player.get_port()))


print("Aguardando outros jogadores...")
player.say_hi(network.socket)

exit(1)

# shuffling & dealing
if player.main:
    input("press anything to start shuffling: ")
    deck = []
    numplayers = player.numplayers
    for i in range(1, 13):
        for j in range(i):
            deck.append(i)

    random.shuffle(deck)
    for i, card in enumerate(deck):
        if i % numplayers == player.index:
            player.receive_card(card)
        else:
            print("player %d gets card %d" % (i % player.numplayers, card))
            sock.sendto(str(card).encode(), (player.get_index(i % numplayers)["ip"], player.get_index(i % numplayers)["port"]))

    for i in range(player.numplayers):
        if i != player.index:
            sock.sendto("endshuffle".encode(), (player.get_index(i % numplayers)["ip"], player.get_index(i % numplayers)["port"]))
else:
    data, addr = sock.recvfrom(1024)
    while (data.decode() != "endshuffle"):
        print("received message:")
        received = data.decode()
        print(received)
        player.receive_card(received)
        data, addr = sock.recvfrom(1024)

print("mycards: ")
print(player.mycards)

# playing
while True:
    if (player.myturn == False):
        data, addr = sock.recvfrom(1024)
        print("received message:")
        print(data.decode(), addr)
        player.set_myturn(True)
    else:
        msg = input("input: ")
        print("sending " + msg + " to:")
        print (player.get_next()["ip"], player.get_next()["port"])
        sock.sendto(msg.encode(), (player.get_next()["ip"], player.get_next()["port"]))
        player.set_myturn(False)
