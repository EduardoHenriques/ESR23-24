import socket
import time
from threading import Thread
import sys, json
from  utils.packet import *
from utils.video_stream import VideoStream
CONFIG_PATH = "Configs/all_routers.json"

class ServerWorker(Thread):
    def __init__(self, name, is_rendezvous, ip, port_UDP, port_TCP, neighbours, extra_info):
        self.port_UDP = port_UDP
        self.port_TCP = port_TCP
        self.ip = ip
        self.device_name = name
        self.RP = is_rendezvous
        self.neighbours = neighbours
        self.extra_info = extra_info
    

    def __str__(self) -> str:
        return (f"Server Worker of device {self.device_name}\nPorts(UDP | TCP): {self.port_UDP} | {self.port_TCP}\nRP: {self.RP}\nIPV4: {self.ip}\nNeighbours: {self.neighbours}")

    def send_media(self, socket, addr): 
        video = VideoStream(self.extra_info)
        while True:              
            # Stop sending if request is PAUSE or TEARDOWN
            data = video.nextFrame()
            if data:
                frameNumber = data.frameNnr()
                try:
                    print((frameNumber, data))
                    CTT.send_msg_udp(Packet(PacketType.MEDIA_REQUEST, (frameNumber, data)), socket, addr)
                except:
                    print("Connection Error")
                    print('-'*60)
                    #traceback.print_exc(file=sys.stdout)
                    print('-'*60)
        # Close the RTP socketself.clientInfo['rtpSocket'].close()print("All done!")
    
    def process_UDP(self, packet, addr):
        print("process")
        #TODO receber media_responses e reencaminhar pacotes recebidos
    # Flooding -> Performs flooding on every router except the one that sent the packet
    # Media -> Redirects the media to the host that requested it or to the server
    
    def process_TCP(self, client_socket,client_address):
        packet = CTT.recv_msg(client_socket)
        while packet != None:
            print(packet)
            # REQ - FLOOD
            if packet.type == PacketType.FLOOD_REQUEST:
                print(f"flood request from {client_address} to {self.device_name}.")
                data = packet.data
                data[0].append(self.ip) # increase path
                if self.RP:
                    data[1] = True # has it reached a RP? 
                else:
                    new_request_packet = Packet(PacketType.FLOOD_REQUEST, data)
                    #TODO criar ligações com todos os vizinhos
                    for n in self.neighbours:
                        CTT.send_msg(new_request_packet, )
                packet_response = Packet(PacketType.FLOOD_RESPONSE, data)
                #TODO enviar resposta para quem fez o pedido
            # RESP - FLOOD
            elif packet.type == PacketType.FLOOD_RESPONSE:
                print(f"flood response from {client_address}")
                data = packet.data
                if data[3] == True:
                    print("....") #TODO
                    
            # REQ - MEDIA   
            elif packet.type == PacketType.MEDIA_REQUEST:
                print(f"media request from {client_address}")
                if "router" not in self.extra_info:
                    print("...")
                self.send_media(client_socket, client_address)
            # RESP - MEDIA
            else:
                print(f"media response from {client_address}")
                # processar response
            packet = CTT.recv_msg(client_socket)
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



    #TODO Flood --> Smp q chega ao RP, response com flag de end of the line
    #TODO Routers must know, who they send the Flood Req & When all of them answer(end) you answer(end) 2