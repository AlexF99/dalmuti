import socket
from network import Network
from message import Message
import random
import pickle
import os

while True:
    clear = lambda: os.system('clear')
    clear()

    network = Network()

    address = socket.gethostbyname(socket.gethostname())
    player = network.get_chair(address)

    # shuffling & dealing
    if (player.main == 1):
        input("press anything to start shuffling: ")

        deck = []
        for i in range(1, 13):
            for j in range(i):
                deck.append(i)
        deck.extend([13, 13])
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

    # playing
    while True:
        if (network.num_players <= 1 or player.end_hand):
            print("ACABOU TUDO")
            break
        if (player.myturn):
            valid_play = False
            choice = 0
            numcards = 0
            while not valid_play:
                print("\nSua vez de jogar!")
                print(f"Suas cartas são:\n{player.mycards}\n")
                if player.round_starter:
                    message = Message(player.id, player.ip, player.ip, "roundwin", "", "")
                    network.socket.sendto(pickle.dumps(message), network.get_next(player))
                    while True:
                        raw_data = network.socket.recv(4096)
                        data = pickle.loads(raw_data)
                        if (data and data.dest == player.ip and data.type == "roundwin"):
                            print("Comecando um novo round\n")
                            player.last_play = {"set": 0, "card": 0}
                            player.get_stick()
                            break

                    choice = int(input("Escolha sua carta (escolha 20 para passar): "))

                    if choice != 20:
                        numcards = int(input(f"Quantos {choice}'s você quer jogar? "))


                else:
                    numcards = int(player.last_play["set"])
                    choice = int(input("Escolha sua carta (escolha 20 para passar): "))
                
                if (choice == 20):
                    print("Você passou a vez")
                    message = Message(player.id, player.ip, player.ip, "play", "pass", "")
                    network.socket.sendto(pickle.dumps(message), network.get_next(player))
                    valid_play = True
                else:
                    has_jester = player.mycards.count(13)
                    play_jester = False
                    last_set = int(player.last_play['set'])
                    last_card = int(player.last_play['card'])

                    occurences = player.mycards.count(choice)
                    
                    if (has_jester > 0 and choice != 13 and (last_set - occurences) == 1):
                        answer = input("Deseja acrescentar um coringa à jogada? (y/n) ")
                        if (answer == "y"):
                            play_jester = True
                            occurences = player.mycards.count(choice) + 1

                    if int(player.last_play['set']) > 0 and (occurences == 0 or numcards < 1 or numcards > occurences):
                        print(f"Você deve jogar {player.last_play['set']} cartas.")
                        continue
                    
                    if (last_card > 0 and choice >= last_card):
                        print(f"Você deve jogar uma carta de valor menor que {last_card}")
                        continue

                    valid_play = True
                    i=0

                    if (play_jester):
                        while i < numcards-1:
                            player.mycards.remove(choice)
                            i = i + 1

                        if (int(player.last_play['set']) == 0):
                            numcards += 1

                        player.mycards.remove(13)
                    else:
                        while i < numcards:
                            player.mycards.remove(choice)
                            i = i + 1

                    if len(player.mycards) == 0:
                        print(f"\n\nAcabou as cartas! Você ficou em {player.rank + 1}o lugar\n")
                        message = Message(player.id, player.ip, player.ip, "gamewin", f"{numcards}:{choice}", "")
                        network.socket.sendto(pickle.dumps(message), network.get_next(player))
                        player.end_hand = True
                        break
                    else:
                        print(f"Você jogou {numcards} da carta {choice}")
                        message = Message(player.id, player.ip, player.ip, "play", f"{numcards}:{choice}", "")
                        network.socket.sendto(pickle.dumps(message), network.get_next(player))

            player.round_starter = False
            while True:
                raw_data = network.socket.recv(4096)
                data = pickle.loads(raw_data)
                if (data and data.dest == player.ip and (data.type == "play" or data.type == "gamewin")):
                    message = Message(player.id, player.ip, network.get_next_player(player).ip, "stick", "", "")
                    network.socket.sendto(pickle.dumps(message), network.get_next(player))
                    player.drop_stick()
                    break

        else:
            print("Aguarde sua vez para jogar...")
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
                    else:
                        player.consecutive_passes = 0
                        print(f"Jogador {data.owner} enviou carta {data.play[0]}")
                        play = data.play[0].split(":")
                        player.last_play = {"set": play[0], "card": play[1]}
                    network.socket.sendto(raw_data, network.get_next(player))
                
                elif (data.dest == player.ip and data.type == "stick"):
                    player.get_stick()

                elif (data.dest != player.ip and data.type == "roundwin"):
                    player.last_play = {"set": 0, "card": 0}
                    player.consecutive_passes = 0
                    player.round_starter = False
                    network.socket.sendto(raw_data, network.get_next(player))

                elif (data.type == "gamewin"):
                    player.consecutive_passes = 0
                    print(f"Jogador {data.owner} enviou carta {data.play[0]}")
                    play = data.play[0].split(":")
                    player.last_play = {"set": play[0], "card": play[1]}
                    print(f"player {data.owner} ganhou o jogo :(\n")
                    player.rank = player.rank + 1
                    network.socket.sendto(raw_data, network.get_next(player))
                    network.remove_player(int(data.owner))  
