from message import Message
import pickle

class Player:
    def __init__(self, ip, port, dealer):
        self.mycards = []
        self.ip = ip
        self.port = port
        self.next = None
        self.myturn = False
        self.main = dealer
    
    def say_hi(self, socket):
        message = Message(self.ip, self.ip, "hi", "", "nsei")
        while True:
            socket.sendto(pickle.dumps(message), (self.next.ip, self.next.port))
            raw_data = socket.recv(4096)
            data = pickle.loads(raw_data)

            if ((data.origin == self.ip and data.dest == self.ip) or (data.type == "endhi")):
                message = Message(self.ip, self.next.ip, "endhi", "", "")
                socket.sendto(pickle.dumps(message), (self.next.ip, self.next.port))
                break

            socket.sendto(raw_data, (self.next.ip, self.next.port))
            

    def get_local(self):
        return {"ip": self.ip, "port": self.port}
    
    def set_myturn(self, toggle):
        self.myturn = toggle

    def get_port(self):
        return self.port
    
    def get_next(self):
        return {"ip": self.next.ip, "port": self.next.port}
    
    def get_index(self, index):
        if index > self.numplayers - 1 or index < 0:
            raise Exception("Index out of range")
        config = self.config[index]
        return {"ip": config[1], "port": config[2]}
    
    def receive_card(self, card):
        self.mycards.append(int(card))