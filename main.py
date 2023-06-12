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
            network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))
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
        valid_play = False
        choice = 0
        numcards = 0
        while not valid_play:
            if player.round_starter:
                choice = int(input("Escolha sua carta (escolha 20 para passar): "))
                if choice != 20:
                    print("quantos %d's voce quer jogar?" % choice)
                    numcards = int(input())
            else:
                print(player.last_play["set"])
                numcards = int(player.last_play["set"])
                choice = int(input("Escolha sua carta (escolha 20 para passar): "))
            
            if (choice == 20):
                print(f"Você passou a vez")
                message = Message(player.id, player.ip, player.ip, "play", "pass", "")
                network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))
                valid_play = True
            else:
                occurences = player.mycards.count(choice)
                if occurences == 0 or numcards < 1 or numcards > occurences:
                    continue
                
                valid_play = True
                i=0
                while i < numcards:
                    player.mycards.remove(choice)
                    i = i + 1

                print(player.mycards)
                print(f"Você jogou {numcards} da carta {choice}")
                message = Message(player.id, player.ip, player.ip, "play", f"{numcards}:{choice}", "")
                network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))

        player.round_starter = False
        while True:
            raw_data = network.socket.recv(4096)
            data = pickle.loads(raw_data)

            if (data):
                if (data.dest == player.ip and data.type == "play"):
                    print("Passou por todo mundo")
                    message = Message(player.id, player.ip, player.next.ip, "stick", "", "")
                    network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))
                    player.drop_stick()
                    break

    else:
        raw_data = network.socket.recv(4096)
        data = pickle.loads(raw_data)

        if (data):
            if (data.dest != player.ip and data.type == "play"):
                if data.play[0] == "pass":
                    player.consecutive_passes = player.consecutive_passes + 1
                    print(f"Jogador {data.owner} passou a vez")
                    print(player.consecutive_passes)
                    if player.consecutive_passes >= network.num_players-1:
                        print("ganhei")
                        player.round_starter = True
                        player.consecutive_passes = 0
                        message = Message(player.id, player.ip, player.ip, "roundwin", "", "")
                        network.socket.sendto(pickle.dumps(message), (player.next.ip, player.next.port))
                        while True:
                            raw_data = network.socket.recv(4096)
                            data = pickle.loads(raw_data)

                            if (data and data.dest == player.ip and data.type == "roundwin"):
                                print("Todos sabem que eu ganhei a rodada")
                                player.get_stick()
                else:
                    player.consecutive_passes = 0
                    print(f"Jogador {data.owner} enviou carta {data.play[0]}")
                    play = data.play[0].split(":")
                    player.last_play = {"set": play[0], "card": play[1]}
                network.socket.sendto(raw_data, (player.next.ip, player.next.port))
            
            elif (data.dest == player.ip and data.type == "stick"):
                print("Bastão passado")
                player.get_stick()

            elif (data.dest != player.ip and data.type == "roundwin"):
                player.last_play = {"set": 0, "card": 0}
                player.consecutive_passes = 0
                player.round_starter = False
