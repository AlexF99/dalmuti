class Message:
    def __init__(self, origin, dest, m_type, play, confirm):
        self.begin= "inicio"
        self.origin = origin
        self.dest = dest
        self.type = m_type
        self.play = play,
        self.confirm = confirm
        self.end = "end"