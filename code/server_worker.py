import socket
import time
from threading import Thread
import sys, json
from  utils.packet import *

CONFIG_PATH = "Configs/all_routers.json"

class ServerWorker(Thread):
    # object -> router OU server
    def __init__(self, name, is_rendezvous, ip, port_UDP, port_TCP, neighbours):
        self.port_UDP = port_UDP
        self.port_TCP = port_TCP
        self.ip = ip
        self.device_name = name
        self.RP = is_rendezvous
        self.neighbours = neighbours
    

    def __str__(self) -> str:
        return (f"Server Worker of device {self.device_name}\n. Ports(UDP | TCP): {self.port_UDP} | {self.port_TCP}\nRP: {self.RP}\nIPV4: {self.ip}\nNeighbours: {self.neighbours}")

    def process_UDP(self, packet, addr):
        if packet.type == "MEDIA_RESPONSE":
            
            
            
    # Flooding -> Performs flooding on every router except the one that sent the packet
    # Media -> Redirects the media to the host that requested it or to the server
    def process_TCP(self, client_socket,client_address):
        while client_socket.fileno() != -1:
            packet = CTT.recv_msg(client_socket)
            if packet.type == PacketType.FLOOD_REQUEST:
                print(f"flood request from {client_address}")
                # processar request
            elif packet.type == PacketType.FLOOD_RESPONSE:
                print(f"flood response from {client_address}")
                # processar response
            elif packet.type == PacketType.MEDIA_REQUEST:
                print(f"media request from {client_address}")
                # processar request
            else:
                print(f"media response from {client_address}")
                # processar response

    def run(self):
        if len(sys.argv) != 1:
            print("Erro - parametros invalidos")
            exit()
        else:
            args = sys.argv[1:]
            router_name = args[0]
            with open(CONFIG_PATH,'r') as file:
                data = json.load(file)
        try:
            while True:
                if(self.type == "TCP"): # TCP => FLOODING
                    break
                if(self.type == "UDP"): # UDP => STREAMING
                    break
        except KeyboardInterrupt:
            self.socket.close()