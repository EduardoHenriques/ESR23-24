from enum import Enum


def class PacketType(Enum):
    # FLOODING
    FLOODING_REQUEST        = 10  
    FLOODING_RESPONSE       = 20
    
    # MEDIA
    MEDIA_REQUEST           = 11
    MEDIA_RESPONSE          = 21  
    

def class Packet():
    # packet vazio
    def __init__(self):
        self.type = None
        self.data = None
        self.sender = None # host original que enviou o pedido
        self.next = None # ip do proximo node p/ enviar a stream
        self.path = [] # stack
        self.jumps = 0
        
    #packet c/ parametros
    def __init__(self, type, data, sender_ip):
        self.type = type
        self.data = data
        self.sender = sender_ip
        if type == FLOODING_REQUEST or type == FLOODING_RESPONSE:
            self.path = [] # stack
        else:
            self.path = None
        self.next = None
        self.jumps = 0
    # obter tipo de packet
    def get_type(self):
        if packet.type == MEDIA_REQUEST:
            return "media request"
        elif packet.type == MEDIA_RESPONSE:
            return "media response"
        elif packet.type == FLOODING_REQUEST:
            return "flooding request"
        elif packet.type == FLOODING_RESPONSE:
            return "flooding response"
        else return "Packet Inválido"
    
    def update(self, new_host):
        self.jumps += 1
        self.path.push(new_host)


