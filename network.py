import socket
from player import Player

class Network:
    def __init__(self):
        self.num_players = 0
        self.connected_players = 0
        self.players = []
        self.socket = None

        config_file = open("config.txt", "r")
        self.num_players = int(config_file.readline().split(":")[1])

        for i in range(self.num_players):
            cfgline = config_file.readline()
            cfgline = cfgline.split(" ")
            addr = cfgline[1].split(":")[1]
            port = int(cfgline[2].split(":")[1])
            dealer = int(cfgline[3].split(":")[1])

            new_player = Player(i, addr, port, dealer)

            if (dealer):
                new_player.get_stick()

            self.players.append(new_player)

        for i, player in enumerate(self.players):
            if (i < self.num_players - 1):
                player.next = self.players[i+1]
            else:
                player.next = self.players[0]
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        config_file.close()
    
    def get_chair(self, ip) -> Player:
        for player in self.players:
            if (player.ip == ip):
                self.socket.bind((player.ip, player.port))
                return player

        print("Player não encontrado") 
