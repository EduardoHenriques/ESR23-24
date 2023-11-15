from utils.packet import *
import time
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
        self.paths = [] # updated(appended) in receive_flood_response
    
    def send_Flood_Req(self):
        packet = Packet(PacketType.FLOOD_REQUEST, [[self.my_ip], False]) # (#jumps, path)
        self.client_TCP.send(packet.encode())
    # N packets flood_response
    # sort p/ jumps
    # send_media_request
    # 
    
    def send_Media_Req(self, video_name, flood_responses):
        #for camiinho in target_info
        #try
        CTT.send_msg(Packet(PacketType.MEDIA_REQUEST, ""),self.client_TCP)
        #paths = sort_paths(flood_responses)
        #for path in paths:
        #    try:
        #        target = path[0]
        #        path.pop(0)
        #        data = (path, video_name)
        #        packet = Packet(PacketType.MEDIA_REQUEST, data)
        #        self.client_TCP.sendto(packet.encode())
        #        break
        #    except:
        #        print("uncussessfull")

    def recv_media(self) :
        start_time = time.time()
        while True:
            packet = CTT.recv_msg_udp(self.client_UDP)
            packet = packet[0]
            if packet and packet.type == PacketType.MEDIA_RESPONSE:
                print (packet.data[0], packet.data[1])
            elapsed_time = time.time() - start_time()
            if elapsed_time > self.TIMEOUT:
                print("CONNECTION TIMEOUT")
                break

    def send_Media_Shutdown(self, video_name, target_info):
        packet = Packet(PacketType.SHUT_DOWN_REQUEST, video_name)
        self.client_TCP.sendto(packet.encode())


def sort_paths(flood_responses):
    #filter flood responses by full paths and removes the auxiliar flag
    true_paths = [packet[0] for packet in flood_responses if packet[1]]
    #sorte the paths by len (number of jumps)
    true_paths =  sorted(true_paths, key=lambda x: len(x))
    return true_paths
