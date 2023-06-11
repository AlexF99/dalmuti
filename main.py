import socket
from player import Player
from network import Network
from message import Message
import random
import pickle

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
print(f"i am a dealer? {player.main}")

print("Aguardando outros jogadores...")
player.say_hi(network.socket)

# shuffling & dealing
if player.main == 1:
    input("press anything to start shuffling: ")

    deck = []
    for i in range(1, 13):
        for j in range(i):
            deck.append(i)
    random.shuffle(deck)

    for i, card in enumerate(deck):
        next_player = network.players[i % network.num_players]
        
        if (next_player == player):
            player.receive_card(card)
        else:
            message = Message(player.ip, next_player.ip, "suffle", card, "")
            network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))

            while True:        
                raw_data = network.socket.recv(4096)
                data = pickle.loads(raw_data)

                print(data)

                if (data.dest == player.ip and data.type == "confirm_shuffle"):
                    break

        # if i % numplayers == player.index:
        #     player.receive_card(card)
        # else:
        #     print("player %d gets card %d" % (i % player.numplayers, card))
        #     sock.sendto(str(card).encode(), (player.get_index(i % numplayers)["ip"], player.get_index(i % numplayers)["port"]))

    for next_player in network.players[-1]:
        if next_player != player:
            message = Message(player.ip, next_player.ip, "end_shuffle", "", "")
            network.socket.sendto(pickle.dumps(message), (next_player.ip, next_player.port))
else:
    while True:
        raw_data = network.socket.recv(4096)
        data = pickle.loads(raw_data)

        print(data.type)

        if (data): 
            if (data.dest == player.ip and data.type == "shuffle"):
                print(f"Card {data.play} received")
                player.receive_card(data.play)
                message = Message(player.ip, data.origin, "confirm_shuffle", "", "")
                network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))

            elif (data.dest != player.ip):
                network.socket.sendto(raw_data, (player.next.ip, player.next.port))

            elif (data.dest == player.ip and data.type == "end_shuffle"):
                break

        data = None


print("mycards: ")
print(player.mycards)

exit(1)

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
