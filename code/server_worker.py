import socket
import threading
import time
from threading import Thread
import sys, json
import traceback
from  utils.packet import *
from utils.video_stream import VideoStream
CONFIG_PATH = "Configs/all_routers.json"
import pprint

class ServerWorker(Thread):
    def __init__(self, name, is_rendezvous, ip, port_UDP, port_TCP, neighbours, extra_info):
        self.port_UDP = port_UDP
        self.port_TCP = port_TCP
        self.ip = ip
        self.device_name = name
        self.RP = is_rendezvous
        self.neighbours = neighbours
        self.extra_info = extra_info
        self.paths = {}
        self.send_to = {} #might not be the real client we are sending to, it's just a way to keep the flux 
    

    def __str__(self) -> str:
        return (f"Server Worker of device {self.device_name}\nPorts(UDP | TCP): {self.port_UDP} | {self.port_TCP}\nRP: {self.RP}\nIPV4: {self.ip}\nNeighbours: {self.neighbours}")

    def send_media_server(self, addr, info): 
        client_ip, video_name = info
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
        UDP_socket.bind((self.ip, int(self.port_UDP)))  # dar bind ao ao ip e porta ao servidor
        video = VideoStream(video_name)
        print(f"adr_client: {addr}, port_udp:{self.port_UDP}")
        ip_cliente, porta = addr
        while True:  
            time.sleep(0.05)            
            # Stop sending if request is PAUSE or TEARDOWN
            data = video.nextFrame()
            if data:
                frameNumber = video.frameNbr()
                try:
                    #print((frameNumber, data))
                    print(f"FRAME N: {frameNumber} being sent...")
                    packet = Packet(PacketType.MEDIA_RESPONSE, [(frameNumber, data), client_ip])
                    addr_port = (ip_cliente, int(self.port_UDP))
                    # packet = CTT.serialize(packet) # transform packet into bytes...
                    #print(f"Type of Object: {type(packet)} -> {type(CTT.serialize(packet))}")
                    CTT.send_msg_udp(packet, UDP_socket, addr_port)
                except Exception as e:
                    #print("Connection Error")
                    print('-'*60)
                    print(f"Raised exception: {e}")
                    traceback.print_exc()
                    print('-'*60)
                    break
        UDP_socket.close()
        # Close the RTP socketself.clientInfo['rtpSocket'].close()print("All done!")

    def send_media_router(self, addr): 
        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
        UDP_socket.bind((self.ip, int(self.port_UDP)))  # dar bind ao ao ip e porta ao servidor
        video = VideoStream(self.extra_info)
        print(f"adr_client: {addr}, port_udp:{self.port_UDP}")
        ip_cliente, porta = addr
        while True:  
            time.sleep(0.05)            
            # Stop sending if request is PAUSE or TEARDOWN
            data = video.nextFrame()
            if data:
                frameNumber = video.frameNbr()
                try:
                    #print((frameNumber, data))
                    print(f"FRAME N: {frameNumber} being sent...")
                    packet = Packet(PacketType.MEDIA_RESPONSE, [(frameNumber, data)])
                    addr_port = (ip_cliente, int(self.port_UDP))
                    # packet = CTT.serialize(packet) # transform packet into bytes...
                    #print(f"Type of Object: {type(packet)} -> {type(CTT.serialize(packet))}")
                    CTT.send_msg_udp(packet, UDP_socket, addr_port)
                except Exception as e:
                    #print("Connection Error")
                    print('-'*60)
                    print(f"Raised exception: {e}")
                    traceback.print_exc()
                    print('-'*60)
                    break
        UDP_socket.close()
        # Close the RTP socketself.clientInfo['rtpSocket'].close()print("All done!")    
    
    def process_UDP(self, packet, addr):
        print("process")
        if packet.type == PacketType.MEDIA_RESPONSE:
            data = packet.data
            frame, ip_cliente = data[0], data[1]
            ip_router = self.best_router(self.paths[ip_cliente])
            UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
            UDP_socket.bind((self.ip, int(self.sw.port_UDP+1)))
            CTT.send_msg_udp(packet, UDP_socket,(ip_router, self.port_UDP))
            UDP_socket.close()
        #TODO receber media_responses e reencaminhar pacotes recebidos
    # Flooding -> Performs flooding on every router except the one that sent the packet
    # Media -> Redirects the media to the host that requested it or to the server
    
    def recv_flood_response(self, response_socket, request_socket):
        while True:
            try:
                packet = CTT.recv_msg(response_socket)        
                p_type, p_data = packet.type, packet.data
                if packet.type == PacketType.FLOOD_RESPONSE:
                    #print(f" P_DATA: {type(p_data[0])} | {p_data[0]}")
                    self.update_path(p_data[0])
                    p_data[0] = self.paths
                    if p_data[1]:
                        print("#" *10 + "VIZINHO CHEGOU AO RP" + "#" *10)
                        CTT.send_msg(packet, request_socket)
                        break
                    CTT.send_msg(packet, request_socket)
            except Exception as e:
                #print("Connection Error")
                print('-'*60)
                print(f"Raised exception: {e}")
                traceback.print_exc()
                print('-'*60)
                break
        response_socket.close()



    def process_TCP(self, request_socket,request_address):
        packet = CTT.recv_msg(request_socket)
        while packet != None:
            #print(packet.type)
            # REQ - FLOOD
            if packet.type == PacketType.FLOOD_REQUEST:
                data = packet.data
                print(f"data: {data[0]}")
                print(f"paths: {self.paths}")
                if self.paths:
                    self.update_path(data[0])
                else:
                    self.paths = data[0]
                #print(f"flood request from {request_address} to {self.device_name}.")
                ip_of_request, _ = request_address
                if ip_of_request not in self.paths:
                    self.paths[ip_of_request] = [[ip_of_request]]
                    print(f"dicionario criado no router -> {self.paths}")
                print("############ BEFORE INSERT##################")
                pp = pprint.PrettyPrinter(indent = 6)
                pp.pprint(self.paths)
                self.insert_ip(self.paths)
                print("############ AFTER INSERT##################")
                pp.pprint(self.paths)
                data[0] = self.paths
               
                if self.RP == "True":
                    print("É RP")
                    data[1] = True # has it reached a RP? 
                    packet_response = Packet(PacketType.FLOOD_RESPONSE, data)
                    CTT.send_msg(packet_response, request_socket)
                    print("-"*20 +"\nRESPOSTA ENVIADA")
                    request_packet = Packet(PacketType.MEDIA_REQUEST, data[3])
                    self.send_media_req(request_packet)
                    break
                else:
                    new_request_packet = Packet(PacketType.FLOOD_REQUEST, data)
                    #TODO criar ligações com todos os vizinhos
                    print("enviar request para os vizinhos")
                    new_port = int(self.port_TCP) + 1
                    #print(f"Current path: {data[0]}")
                    i = 1
                    for n in self.neighbours:
                        if n != ip_of_request:
                            time.sleep(0.5)
                            print(f"ligar ao vizinho:{n}")
                            adress_for_neighbours = (self.ip, new_port)
                            # criar socket
                            neighbours_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            neighbours_socket.bind(adress_for_neighbours)
                            #print(f"Connection to{n}, in port {self.port_TCP}")
                            neighbours_socket.connect((n, int(self.port_TCP)))
                            CTT.send_msg(new_request_packet, neighbours_socket)
                            nt = threading.Thread(target=self.recv_flood_response, args=(neighbours_socket,request_socket))
                            nt.start()
                            #print(f"PACKET {i} SENT")
                            i+=1
                            new_port +=1
                    #print("enviar resposta de volta")
                    packet_response = Packet(PacketType.FLOOD_RESPONSE, data)
                    CTT.send_msg(packet_response, request_socket)
                    if send_to:
                        client_ip, video_name= data[3]
                        for ip, streamed_video in send_to.items():
                            if streamed_video == video_name:
                                send_to[client_ip] = video_name
                #TODO enviar resposta para quem fez o pedido
            # RESP - FLOOD
            elif packet.type == PacketType.FLOOD_RESPONSE:
                print(f"flood response from {request_address}")
                data = packet.data
                if data[3] == True:
                    print("....") #TODO
                    
            # REQ - MEDIA   
            elif packet.type == PacketType.MEDIA_REQUEST:
                print(f"media request from {request_address}")
                if "server" in self.extra_info:
                    time.sleep(2)
                    self.send_media_server(request_address,packet.data[3])
                else:
                    print(..)
            # RESP - MEDIA
            else:
                print(f"media response from {request_address}")
                # processar response
            packet = CTT.recv_msg(request_socket)
        request_socket.close()
    def run(self):
        if len(sys.argv) != 1:
            print("Erro - parametros invalidos")
            exit()
        else:
            args = sys.argv[1:]
            router_name = args[0]
            with open(CONFIG_PATH,'r') as file:
                data = json.load(file)
        #try:
        #    while True:
        #        if(self.type == "TCP"): # TCP => FLOODING
        #            break
        #        if(self.type == "UDP"): # UDP => STREAMING
        #            break
        #except KeyboardInterrupt:
        #    self.socket.close()

    def end(self):
        self.socket.close()
    
    # takes a dictionary {<IP> : [<PATH>]} from the flood request that the node received
    # and updates its own dictionary with it.
    # This must be done before sending its own dictionary to the other nodes.
    def update_path(self, path_dict):
        #print("############ BEFORE UPDATE##################")
        #pp = pprint.PrettyPrinter(indent = 6)
        #pp.pprint(self.paths)
        #print(f"dicionario antes da adição: {self.paths}")
        for key, value in path_dict.items():
            if key != self.ip:
                if key not in self.paths:
                    self.paths[key] = value # add a new key,value pair if IP is unknown 
                else:
                    for path in value:
                        if path not in self.paths[key]: # update its paths with the current node's IP if 1 or more paths were known previously
                            print("-"*20)
                            print(f"valor a adicionar {path}")
                            self.paths[key].append(path)
                            print("-"*20)
        #print("############ AFTER UPDATE##################")
        #pp.pprint(self.paths)
        #print(f"dicionario dps da adição: {self.paths}")
    
    def insert_ip(self, p_dict):
        for key, value in p_dict.items():
            for path in value:
                if self.ip not in path:
                    path.insert(0,self.ip)
        self.path = p_dict
    
    def send_media_req(self, new_request_packet):
        adress_for_server = (self.ip, self.port_TCP+1)
        # criar socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(adress_for_server)
        #print(f"Connection to{n}, in port {self.port_TCP}")
        server_socket.connect((self.ip_server, int(self.port_TCP)))
        CTT.send_msg(new_request_packet, server_socket)
    
    def best_router(self, list_of_paths):
        return list_of_paths[1]
    #TODO Flood --> Smp q chega ao RP, response com flag de end of the line
    #TODO Routers must know, who they send the Flood Req & When all of them answer(end) you answer(end) 2