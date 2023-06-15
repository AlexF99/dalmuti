class Player:
    def __init__(self, player_id, ip, port, dealer):
        self.end_hand = False
        self.mycards = []
        self.id = player_id
        self.rank = 0
        self.ip = ip
        self.port = port
        self.main = dealer
        self.myturn = False
        self.round_starter = dealer
        self.last_play = {"set": 0, "card": 0}
        self.consecutive_passes = 0

    def get_local(self):
        return {"ip": self.ip, "port": self.port}
    
    def get_stick(self):
        self.myturn = True

    def drop_stick(self):
        self.myturn = False

    def get_port(self):
        return self.port
    
    def get_index(self, index):
        if index > self.numplayers - 1 or index < 0:
            raise Exception("Index out of range")
        config = self.config[index]
        return {"ip": config[1], "port": config[2]}
    
    def receive_card(self, card):
        self.mycards.append(int(card))