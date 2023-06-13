import socket
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
print("my port is: " + str(player.get_port()))
print(f"i am a dealer? {player.main}")

print("Aguardando outros jogadores...")

# message = Message(self.id, self.ip, self.ip, "hi", "", "nsei")
# while True:
#     socket.sendto(pickle.dumps(message), (self.next.ip, self.next.port))
#     raw_data = socket.recv(4096)
#     data = pickle.loads(raw_data)

#     if ((data.origin == self.ip and data.dest == self.ip) or (data.type == "endhi")):
#         message = Message(self.id, self.ip, self.next.ip, "endhi", "", "")
#         socket.sendto(pickle.dumps(message), (self.next.ip, self.next.port))
#         break

#     socket.sendto(raw_data, (self.next.ip, self.next.port))

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
            network.socket.sendto(pickle.dumps(message), network.get_next(player))

            while True:        
                raw_data = network.socket.recv(4096)
                data = pickle.loads(raw_data)

                if (data.dest == player.ip and data.type == "confirm_shuffle"):
                    break

    for next_player in reversed(network.players):
        if next_player != player:
            message = Message(player.id, player.ip, next_player.ip, "end_shuffle", "", "")
            network.socket.sendto(pickle.dumps(message), network.get_next(player))

    player.mycards.sort()
else:
    while True:
        raw_data = network.socket.recv(4096)
        data = pickle.loads(raw_data)

        print(data.type)

        if (data): 
            if (data.dest == player.ip and data.type == "shuffle"):
                player.receive_card(data.play[0])
                message = Message(player.id, player.ip, data.origin, "confirm_shuffle", "", "")
                network.socket.sendto(pickle.dumps(message), network.get_next(player))

            elif (data.dest != player.ip):
                network.socket.sendto(raw_data, network.get_next(player))

            elif (data.dest == player.ip and data.type == "end_shuffle"):
                break

        data = None
    player.mycards.sort()

print("mycards: ")
print(player.mycards)

# playing
while True:
    print("is it my turn: ")
    print(player.myturn)
    if (player.myturn):
        valid_play = False
        choice = 0
        numcards = 0
        while not valid_play:
            print(player.mycards)
            if player.round_starter:
                message = Message(player.id, player.ip, player.ip, "roundwin", "", "")
                network.socket.sendto(pickle.dumps(message), network.get_next(player))
                while True:
                    raw_data = network.socket.recv(4096)
                    data = pickle.loads(raw_data)
                    if (data and data.dest == player.ip and data.type == "roundwin"):
                        print("Comecando um novo round")
                        player.get_stick()
                        break
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
                network.socket.sendto(pickle.dumps(message), network.get_next(player))
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

                # player.mycards = [] #remove isso depois pelo amor de deus

                if len(player.mycards) == 0:
                    print(player.mycards)
                    print("\n\nParabéns! Você ganhou essa mao!")
                    message = Message(player.id, player.ip, player.next.ip, "gamewin", "", "")
                    network.socket.sendto(pickle.dumps(message), network.get_next(player))
                else:
                    print(player.mycards)
                    print(f"Você jogou {numcards} da carta {choice}")
                    message = Message(player.id, player.ip, player.ip, "play", f"{numcards}:{choice}", "")
                    network.socket.sendto(pickle.dumps(message), network.get_next(player))

        player.round_starter = False
        while True:
            raw_data = network.socket.recv(4096)
            data = pickle.loads(raw_data)
            if (data and data.dest == player.ip and data.type == "play"):
                print("Passou por todo mundo")
                message = Message(player.id, player.ip, player.next.ip, "stick", "", "")
                network.socket.sendto(pickle.dumps(message), network.get_next(player))
                player.drop_stick()
                break
            elif (data and data.dest == player.ip and data.type == "gamewin"):
                print("Todos sabem que eu ganhei")
                quit()

    else:
        print("up and listening...")
        raw_data = network.socket.recv(4096)
        data = pickle.loads(raw_data)

        if (data):
            print(data.type)
            if (data.dest != player.ip and data.type == "play"):
                if data.play[0] == "pass":
                    player.consecutive_passes = player.consecutive_passes + 1
                    print(f"Jogador {data.owner} passou a vez")
                    print(player.consecutive_passes)
                    if player.consecutive_passes >= network.num_players-1:
                        print("ganhei")
                        player.round_starter = True
                        player.consecutive_passes = 0
                else:
                    player.consecutive_passes = 0
                    print(f"Jogador {data.owner} enviou carta {data.play[0]}")
                    play = data.play[0].split(":")
                    player.last_play = {"set": play[0], "card": play[1]}
                network.socket.sendto(raw_data, network.get_next(player))
            
            elif (data.dest == player.ip and data.type == "stick"):
                print("Bastão passado")
                player.get_stick()

            elif (data.dest != player.ip and data.type == "roundwin"):
                player.last_play = {"set": 0, "card": 0}
                player.consecutive_passes = 0
                player.round_starter = False
                network.socket.sendto(raw_data, network.get_next(player))

            elif (data.type == "gamewin"):
                player.last_play = {"set": 0, "card": 0}
                player.consecutive_passes = 0
                player.round_starter = False
                print(f"player {data.owner} won the game :(")
                network.remove_player(int(data.owner))
                if data.dest == player.ip:
                    player.get_stick()
                else:
                    network.socket.sendto(raw_data, network.get_next(player))

