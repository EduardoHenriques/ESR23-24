from utils.packet import *
from time import time
import socket


class Client():
    # Client connects to router through TCP
    def __init__(self, my_ip, a_router,tcp_p, udp_p):
        self.my_ip = my_ip
        self.client_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client_TCP.connect((a_router, int(tcp_p)))
        self.client_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create UDP socket
        self.client_UDP.bind((my_ip, int(udp_p)))  # bind ip and address
        self.TIMEOUT = 5 # seconds to terminate connection
    
    def send_Flood_Req(self):
        packet = Packet(PacketType.FLOOD_REQUEST, (0, [self.my_ip])) # (#jumps, path)
        self.client_TCP.send(packet.encode())
    
    def send_Media_Req(self, video_name, target_info):
        packet = Packet(PacketType.MEDIA_REQUEST, video_name)
        self.client_TCP.sendto(packet.encode())

    def recv_media(self) -> Packet:
        start_time = time.time()
        while True:
            packet = CTT.recv_msg_udp()
            packet = packet[0]
            if packet and packet.type == PacketType.MEDIA_RESPONSE:
                return (packet.data[0], packet.data[1])
            elapsed_time = time.time() - start_time()
            if elapsed_time > self.TIMEOUT:
                print("CONNECTION TIMEOUT")
                break

    def send_Media_Shutdown(self, video_name, target_info):
        packet = Packet(PacketType.SHUT_DOWN_REQUEST, video_name)
        self.client_TCP.sendto(packet.encode())
