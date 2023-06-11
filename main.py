import socket
from player import Player
from network import Network
from message import Message
import random
import pickle

network = Network()

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
if (player.main == 1):
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
            message = Message(player.id, player.ip, next_player.ip, "shuffle", card, "")
            network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))

            while True:        
                raw_data = network.socket.recv(4096)
                data = pickle.loads(raw_data)

                print(data)

                if (data.dest == player.ip and data.type == "confirm_shuffle"):
                    break

    for next_player in reversed(network.players):
        if next_player != player:
            message = Message(player.id, player.ip, next_player.ip, "end_shuffle", "", "")
            network.socket.sendto(pickle.dumps(message), (next_player.ip, next_player.port))
else:
    while True:
        raw_data = network.socket.recv(4096)
        data = pickle.loads(raw_data)

        print(data.type)

        if (data): 
            if (data.dest == player.ip and data.type == "shuffle"):
                print(f"Card {data.play} received")
                player.receive_card(data.play[0])
                message = Message(player.id, player.ip, data.origin, "confirm_shuffle", "", "")
                network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))

            elif (data.dest != player.ip):
                network.socket.sendto(raw_data, (player.next.ip, player.next.port))

            elif (data.dest == player.ip and data.type == "end_shuffle"):
                break

        data = None


print("mycards: ")
print(player.mycards)

# playing
while True:
    if (player.myturn):
        choice = int(input("Sua vez, escolha sua carta: "))
        card_index = player.mycards.index(choice) if choice in player.mycards else -1
        
        while (card_index == -1):
            choice = int(input("Você não possui essa carta, tente outra. "))
            card_index = player.mycards.index(choice) if choice in player.mycards else -1

        card = player.mycards[card_index]
        print(f"Você escolheu a carta {card}")
        message = Message(player.id, player.ip, player.ip, "play", card, "")
        network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))

        player.mycards.remove(card)
        print(player.mycards)

        while True:
            raw_data = network.socket.recv(4096)
            data = pickle.loads(raw_data)

            if (data):
                if (data.dest == player.ip and data.type == "play"):
                    print("Passou por todo mundo")
                    message = Message(player.id, player.ip, player.next.ip, "pass", "", "")
                    network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))
                    player.drop_stick()
                    break

    else:
        raw_data = network.socket.recv(4096)
        data = pickle.loads(raw_data)

        if (data):
            if (data.dest != player.ip and data.type == "play"):
                print(f"Jogador {data.owner} enviou carta {data.play[0]}")
                network.socket.sendto(raw_data, (player.next.ip, player.next.port))
            
            elif (data.dest == player.ip and data.type == "pass"):
                print("Bastão passado")
                player.get_stick()
