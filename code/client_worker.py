from utils.packet import *
import socket

class Client():
    # Cria um cliente conectado a um router por TCP 
    def __init__(self, my_ip, a_router,tcp_p, udp_p):
        self.client_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client_TCP.connect((a_router, int(tcp_p)))
        self.client_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
        self.client_UDP.bind((my_ip, int(udp_p)))  # dar bind ao ao ip e porta ao servidor
    
    #def stream_connection(self, server, udp_p):
     #   self.client_UDP.bind((my_ip, int(udp_p)))
    #TODO Func send packets, recieve packets
    

