class Config:
    def __init__(self, ip):
        self.ip = ip
        config_file = open("config.txt", "r")
        self.config = []
        self.index = -1
        self.myturn = False
        for i, line in enumerate(config_file):
            if (i == 0):
                self.numplayers = int(line.split(":")[1][:-1])
                continue
            cfgline = line.split(" ")
            addr = cfgline[1].split(":")[1]
            port = cfgline[2].split(":")[1]
            self.config.append((i, addr, int(port)))
            if addr == self.ip:
                self.myturn = bool(int(cfgline[3].split(":")[1][:-1]))
                self.index = i-1
        config_file.close()

    def get_local(self):
        config = self.config[self.index]
        return {"ip": config[1], "port": config[2]}
    
    def get_myturn(self):
        return self.myturn
    
    def set_myturn(self, toggle):
        self.myturn = toggle

    def get_port(self):
        return int(self.config[self.index][2])
    
    def get_next(self):
        index = 0
        if (self.index < self.numplayers - 1):
            index = self.index + 1
        config = self.config[index]
        return {"ip": config[1], "port": config[2]}
    
    def get_prev(self):
        if (self.index > 0):
            return self.config[self.index - 1]
        return self.config[-1]