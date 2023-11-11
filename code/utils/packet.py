from enum import Enum
import pickle


class PacketType(Enum):
    # Pacotes enviados pelos routers
    FLOOD_REQUEST          = 10
    FLOOD_RESPONSE         = 11
    FLOOD_ERROR            = 12 

    # Pacotes enviados entre servidores/clientes 
    MEDIA_REQUEST          = 20
    MEDIA_RESPONSE         = 21
    MEDIA_ERROR            = 22

    # Pacotes enviados para o servidor 
    SHUT_DOWN_REQUEST      = 30
    
class Packet:
    def __init__(self, type, data):
        self.type = type
        self.data = data
    
    def __str__(self) -> str:
        return (f"type: {self.type}\ndata: {self.data}")
class CTT:
    HEADER_SIZE = 8
    BUFFER_SIZE = 1024

    @staticmethod
    def send_msg(msg, sock):
        msg_bytes = CTT.serialize(msg)
        
        msg_len = len(msg_bytes)
        header = msg_len.to_bytes(CTT.HEADER_SIZE, 'big')
        
        sock.sendall(header)

        sock.sendall(msg_bytes)

    @staticmethod
    def send_msg_udp(msg, sock, serverAddressPort):
        msg_bytes = CTT.serialize(msg)
        sock.sendto(msg_bytes, serverAddressPort)


    @staticmethod
    def recv_msg(sock):
        header = sock.recv(CTT.HEADER_SIZE)
        msg_len = int.from_bytes(header, 'big')
        recv_bytes = 0
        msg_bytes = b''
        while recv_bytes < msg_len:
            bytes_left = msg_len - recv_bytes
            if bytes_left < CTT.BUFFER_SIZE:
                buffer = sock.recv(bytes_left)
                recv_bytes += bytes_left
            else:
                buffer = sock.recv(CTT.BUFFER_SIZE)
                recv_bytes += CTT.BUFFER_SIZE
            msg_bytes += buffer
        msg = CTT.deserialize(msg_bytes)
        return msg

    @staticmethod
    def recv_msg_udp(sock):
        bufferSize = 1024
        msg_bytes, adress = sock.recvfrom(bufferSize)
        msg = CTT.deserialize(msg_bytes)
        return (msg, adress)

    @staticmethod
    def serialize(msg):
        return pickle.dumps(msg)

    @staticmethod
    def deserialize(msg_bytes):
        try:
            data = pickle.loads(msg_bytes)
        except EOFError:
            data = None  # or whatever you want

        return data

    
    