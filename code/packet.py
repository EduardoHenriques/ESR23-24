from enum import Enum


class PacketType(Enum):
    # FLOODING
    FLOODING_REQUEST        = 10  
    FLOODING_RESPONSE       = 20
    
    # MEDIA
    MEDIA_REQUEST           = 11
    MEDIA_RESPONSE          = 21  
    

class Packet():
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
        if type == PacketType.FLOODING_REQUEST or type == PacketType.FLOODING_RESPONSE:
            self.path = [] # stack
        else:
            self.path = None
        self.next = None
        self.jumps = 0
    # obter tipo de packet
    def get_type(self):
        if  self.packet.type == PacketType.MEDIA_REQUEST:
            return "media request"
        elif self.packet.type == PacketType.MEDIA_RESPONSE:
            return "media response"
        elif self.packet.type == PacketType.FLOODING_REQUEST:
            return "flooding request"
        elif self.packet.type == PacketType.FLOODING_RESPONSE:
            return "flooding response"
        else:
            return "Packet Inválido"
    
    def update(self, new_host):
        self.jumps += 1
        self.path.push(new_host)


