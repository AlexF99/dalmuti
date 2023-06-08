class Config:
    def __init__(self, ip):
        self.ip = ip
        config_file = open("config.txt", "r")
        self.config = []
        self.index = -1
        for i, line in enumerate(config_file):
            if (i == 0):
                self.numplayers = int(line.split(":")[1][:-1])
                continue
            cfgline = line.split(" ")
            addr = cfgline[1].split(":")[1]
            port = cfgline[2].split(":")[1][:-1]
            self.config.append((i, addr, port))
            print(addr, self.ip, self.ip == addr)
            if addr == self.ip:
                self.index = i-1
        config_file.close()

    def get_local(self):
        return self.config[self.index]

    def get_port(self):
        return int(self.config[self.index][2])
    
    def get_next(self):
        if (self.index < self.numplayers - 1):
            return self.config[self.index + 1]
        return self.config[0]
    
    def get_prev(self):
        if (self.index > 0):
            return self.config[self.index - 1]
        return self.config[-1]