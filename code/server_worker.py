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
    def __init__(self, name, is_rendezvous, ip, port_UDP, port_TCP, neighbours, extra_info,servers_ip):
        self.port_UDP = port_UDP
        self.port_TCP = port_TCP
        self.ip = ip
        self.device_name = name
        self.RP = is_rendezvous
        self.neighbours = neighbours
        self.extra_info = extra_info
        self.paths = {}
        self.send_to = {} #might not be the real client we are sending to, it's just a way to keep the flux 
        self.servers_ip = servers_ip
        self.threads = []
        self.video_from = {}
        self.start_stream = False
        self.listen_udp = True
    

    def __str__(self) -> str:
        return (f"Server Worker of device {self.device_name}\nPorts(UDP | TCP): {self.port_UDP} | {self.port_TCP}\nRP: {self.RP}\nIPV4: {self.ip}\nNeighbours: {self.neighbours}")

    def send_media_server(self, addr, info):
        time.sleep(1) 
        client_ip, video_name = info
        if video_name not in self.send_to.items():
            try:
                print("############# A COMEÇAR STREAM #########################")
                self.send_to[client_ip] = video_name
                UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
                UDP_socket.bind((self.ip, int(self.port_UDP)))  # dar bind ao ao ip e porta ao servidor
                UDP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                video = VideoStream(video_name)
                #print(f"adr_client: {addr}, port_udp:{self.port_UDP}")
                request_ip, porta = addr
                while self.start_stream:    
                    time.sleep(0.05)      
                    # Stop sending if request is PAUSE or TEARDOWN
                    data = video.nextFrame()
                    if data:
                        frameNumber = video.frameNbr()
                        try:
                            #print((frameNumber, data))
                            print(f"FRAME N: {frameNumber} being sent...")
                            packet = Packet(PacketType.MEDIA_RESPONSE, [(frameNumber, data), (client_ip,video_name)])
                            addr_port = (request_ip, int(self.port_UDP))
                            # packet = CTT.serialize(packet) # transform packet into bytes...
                            #print(f"Type of Object: {type(packet)} -> {type(CTT.serialize(packet))}")
                            CTT.send_msg_udp(packet, UDP_socket, addr_port)
                        except Exception as e:
                            #print("Connection Error")
                           # print('-'*60)
                            print(f"Raised exception: {e}")
                            traceback.print_exc()
                            #print('-'*60)
                            break
                    else:
                        break
               # print("STOPING STREAM.....")
                UDP_socket.close()
                print("STREAM CLOSED")
                # Close the RTP socketself.clientInfo['rtpSocket'].close()print("All done!")
            except Exception:
                print("SERVER ALREADY STREAMING")
        
    
    def process_UDP(self, packet, addr):
        if packet.type == PacketType.MEDIA_RESPONSE:
            ip_of_request, _ = addr
            data = packet.data
            frame = data[0]
            client_ip, video_name = data[1]
            if client_ip not in self.send_to.keys():
                #print(f"adicionou o valor again{client_ip}")
                self.send_to[client_ip] = video_name
                pp = pprint.PrettyPrinter(indent = 6)
                pp.pprint(self.send_to)
            if video_name not in self.video_from.keys():
                self.video_from[video_name] = ip_of_request
            for client, video in self.send_to.items():
                if video == video_name: 
                    ip_router = self.best_router(self.paths[client])
                    UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
                    UDP_socket.bind((self.ip, int(self.port_UDP)+1))
                    CTT.send_msg_udp(packet, UDP_socket,(ip_router, int(self.port_UDP)))
                    UDP_socket.close()
    
    def recv_flood_response(self, response_socket, request_socket):
        first = True
        numb_of_neighbours = None
        neighbours_response = 0
        num_packet = Packet(PacketType.FLOOD_INFO, len(self.neighbours))
        CTT.send_msg(num_packet, request_socket)
        while True:  
            try:
                packet = CTT.recv_msg(response_socket)        
                p_type, p_data = packet.type, packet.data
                if p_type == PacketType.FLOOD_INFO:
                    print("number of neighbours response")
                    numb_of_neighbours = p_data
                    if numb_of_neighbours == 0:
                        numb_of_neighbours +=1
                if p_type == PacketType.FLOOD_RESPONSE:
                    #print("RESPONSE")
                    #print(f" P_DATA: {type(p_data[0])} | {p_data[0]}")
                    #pp = pprint.PrettyPrinter(indent = 6)
                    #print("#############BEFORE UPDATE FUNC###############")
                    #pp.pprint(p_data[0])
                    self.update_path(p_data[0])
                    #print("#############AFTER UPDATE FUNC###############")
                    p_data[0] = self.paths
                    #print("CAMINHOS A SER ENVIADOS DE VOLTA")
                    #pp = pprint.PrettyPrinter(indent = 6)
                    #pp.pprint(self.paths)
                    
                    print("-"*20)
                    if p_data[1]:
                        neighbours_response +=1
                        print(f"number of neighbours: {numb_of_neighbours} vs number of responses: {neighbours_response}")
                        print(f"FROM{response_socket.getpeername()}\n TO {request_socket.getpeername()}")
                        print("#" *10 + "VIZINHO CHEGOU AO RP" + "#" *10)
                        CTT.send_msg(packet, request_socket)
                        if numb_of_neighbours == neighbours_response:
                            break
                    CTT.send_msg(packet, request_socket)
            except Exception as e:
                #print('-'*60)
                print(f"Raised exception: {e}")
                traceback.print_exc()
                #print('-'*60)
                break
        print(f"########FECHAR SOCKET##########################")
        response_socket.close()



    def process_TCP(self, request_socket,request_address):
        packet = CTT.recv_msg(request_socket)
        shutdown_ip = None
        while packet != None:
            if packet.type == PacketType.FLOOD_REQUEST:
                print("REQUEST")
                data = packet.data
                if self.paths:
                    self.update_path(data[0])
                else:
                    self.paths = data[0]
                ip_of_request, _ = request_address
                if self.ip not in self.paths:
                    self.paths[self.ip] = [[self.ip]]
                if ip_of_request not in self.paths:
                    self.paths[ip_of_request] = [[ip_of_request]]
                self.insert_ip(self.paths)
                #pp = pprint.PrettyPrinter(indent = 6)
                #pp.pprint(self.paths)
                data[0] = self.paths
               
                if self.RP == "True":
                    client_ip, video_name= data[2]
                    #print("É RP")
                    data[1] = True # has it reached a RP? 
                    num_packet = Packet(PacketType.FLOOD_INFO, 1)
                    CTT.send_msg(num_packet, request_socket)
                    packet_response = Packet(PacketType.FLOOD_RESPONSE, data)
                    #pp = pprint.PrettyPrinter(indent = 6)
                    #pp.pprint(self.paths)
                    CTT.send_msg(packet_response, request_socket)
                    server = self.best_server() 
                    #print("-"*20 +"\nRESPOSTA ENVIADA")
                    request_packet = Packet(PacketType.MEDIA_REQUEST, data[2])
                    self.send_media_req(server,request_packet)
                    break
                else:
                    new_request_packet = Packet(PacketType.FLOOD_REQUEST, data)
                    #print("enviar request para os vizinhos")
                    new_port = int(self.port_TCP) + 1
                    i = 1
                    for n in self.neighbours:
                        if n != ip_of_request:
                            time.sleep(0.5)
                            #print(f"ligar ao vizinho:{n}")
                            # criar socket
                            neighbours_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            neighbours_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            attempts = 0
                            while True:
                                try:
                                    adress_for_neighbours = (self.ip, new_port)
                                    neighbours_socket.bind(adress_for_neighbours)
                                    neighbours_socket.connect((n, int(self.port_TCP)))
                                    CTT.send_msg(new_request_packet, neighbours_socket)
                                    nt = threading.Thread(target=self.recv_flood_response, args=(neighbours_socket,request_socket))
                                    self.threads.append(nt)
                                    nt.start()
                                    i+=1
                                    new_port +=1
                                    break
                                except Exception as e:
                                    #print(f"IN FLOOD_REQUEST: port {new_port} already in use, trying other...")
                                    new_port +=1
                                    attempts +=1
                                    if attempts >10:
                                        break
                    packet_response = Packet(PacketType.FLOOD_RESPONSE, data)
                    print(f"ENVIAR RESPSTA PARA: {request_socket}")
                    CTT.send_msg(packet_response, request_socket)
                    if self.send_to:
                        print("############ JA TEM STREAM ##################")
                        client_ip, video_name= data[2]
                        #try:
                        for ip, streamed_video in self.send_to.items():
                            if streamed_video == video_name:
                                print("############ BEFORE INSERT OF CLIENT##################")
                                pp = pprint.PrettyPrinter(indent = 6)
                                pp.pprint(self.send_to)
                                print("############ AFTER INSERT OF CLIENT##################")
                                self.send_to[client_ip] = video_name
                                pp = pprint.PrettyPrinter(indent = 6)
                                pp.pprint(self.send_to)
                        #except Exception as e:
                        #   print("Failed attempt to piggy-back on existing connection")
            # REQ - MEDIA   
            elif packet.type == PacketType.MEDIA_REQUEST:
                #print(f"media request from {request_address}")
                if "server" in self.extra_info:
                    #time.sleep(0.5)
                    client_ip, video_name = packet.data
                    self.start_stream = True 
                    self.send_media_server(request_address,packet.data)
                    break
                else:
                    print("..")
                #print("END SOCKET FOR MEDIA REQUEST")
                break
            elif packet.type == PacketType.SHUT_DOWN_REQUEST:
                shutdown_ip, video_name = packet.data # shutdown packet data is the IP of the client and the name of the video that they want to shut down
                ip_of_request, _ = request_address
                print(f"RECIEVED A SHUTDOWN REQUEST FROM {ip_of_request}")
                print(f"IP OF CLIENT:{shutdown_ip}\nLIST OF SEND_TO{self.send_to}")
                pp = pprint.PrettyPrinter(indent = 6)
                pp.pprint(self.send_to)
                if shutdown_ip in self.send_to.keys():
                    self.send_to.pop(shutdown_ip)
                    print(f"AFTER POP....\nIP OF CLIENT:{shutdown_ip}")
                    pp = pprint.PrettyPrinter(indent = 6)
                    pp.pprint(self.send_to)
                    if not self.send_to:
                        print(f"if not self.send_to")
                        if self.extra_info != "server": # if the dictionary is empty after removal send the shutdown signal to the server to stop streaming the video
                            print("self.extra_info != server")
                            ip_dest = self.video_from[video_name]
                            shutdown_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            shutdown_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            new_port = int(self.port_TCP) + 1
                            attempts = 0
                            while True:
                                try:
                                    print(f"FOWARDING SHUTDOWN REQUEST TO {ip_dest}")
                                    #print(self.send_to)
                                    adress_for_shutdown = (self.ip, new_port)
                                    shutdown_socket.bind(adress_for_shutdown)
                                    shutdown_socket.connect((ip_dest, int(self.port_TCP)))
                                    CTT.send_msg(packet, shutdown_socket)
                                    #print(f"Forwarding shutdown request... to {ip_dest}")
                                    shutdown_socket.close()
                                    break
                                except Exception as e:
                                    #print(f"IN SHUTDOWN_REQUEST: port {new_port} already in use, trying other...")
                                    new_port +=1
                                    attempts +=1
                                    if attempts >10:
                                        break
                            #shutdown_socket.close()
                        else:
                            self.start_stream = False
                        break
            elif packet.type == PacketType.INFO_REQUEST:
                #print("This is an information request")
                #print(packet.data)
                latency = int(time.time() * 1000) - packet.data
                packet = Packet(PacketType.INFO_REQUEST, latency)
                CTT.send_msg(packet,request_socket)
                break                
            packet = CTT.recv_msg(request_socket)
        print(f"CLOSING SOCKET{request_socket}")    
        request_socket.close()
        print(f"HANDLING THREADS{self.threads}")
        for t in self.threads:
            #print(f"REMOVING THREAD{t}")
            t.join()
        time.sleep(0.05)
        if shutdown_ip in self.send_to.keys():
            #print(f"RESOLVING PROBLEMS..")
            self.send_to.pop(shutdown_ip)
       # print(self.send_to)
    def run(self):
        if len(sys.argv) != 1:
            print("Erro - parametros invalidos")
            exit()
        else:
            args = sys.argv[1:]
            router_name = args[0]
            with open(CONFIG_PATH,'r') as file:
                data = json.load(file)

    def end(self):
        self.socket.close()
    
    # takes a dictionary {<IP> : [<PATH>]} from the flood request that the node received
    # and updates its own dictionary with it.
    # This must be done before sending its own dictionary to the other nodes.
    def update_path(self, path_dict):
        for key, value in path_dict.items():
            if key != self.ip:
                if key not in self.paths:
                    self.paths[key] = value # add a new key,value pair if IP is unknown 
                else:
                    for path in value:
                        if path not in self.paths[key] and path[0] in self.neighbours: # update its paths with the current node's IP if 1 or more paths were known previously
                            #print("-"*20)
                            #print(f"valor a adicionar {path}")
                            self.paths[key].append(path)
                            #print("-"*20)
                    #pp = pprint.PrettyPrinter(indent = 6)
                    #pp.pprint(self.paths)
    def insert_ip(self, p_dict):
        for key, value in p_dict.items():
            for path in value:
                if self.ip not in path :
                    path.insert(0,self.ip)
        self.path = p_dict
    
    def send_media_req(self, server,new_request_packet):
        print("-"*20 +"\TENTAR ENVIAR MEDIA REQUEST....")
        _, video_name= new_request_packet.data
        new_port = int(self.port_TCP) + 1
        attempts = 0
        while True:
            try:
                #print(f"valores:{self.send_to}\nnome{video_name}")
                if video_name not in self.send_to.values():
                    #print("-"*20 +"\ENTROU NO FOR")
                    adress_for_server = (self.ip, new_port)
                    #criar socket
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    server_socket.bind(adress_for_server)
                    server_socket.connect((server, int(self.port_TCP)))
                    CTT.send_msg(new_request_packet, server_socket)
                    print("-"*20 +"\MEDIA REQUEST ENVIADO")
                    server_socket.close()
                else:
                    print("n entrou no if")
                break
            except Exception as e:
                print(f"IN MEDIA_REQUEST: port {new_port} already in use, trying other...")
                print(e)
                new_port += 1
                attempts +=1
                if attempts >10:
                    break


    def best_server(self):
        newb_server = self.servers_ip[0]
        # data -> current time(ms)
        best_time = float('inf')
        new_port = int(self.port_TCP) + 1
        for server in self.servers_ip:
            attempts = 0
            while True:
                try:
                    info_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    info_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    adress_for_neighbours = (self.ip, new_port)
                    info_socket.bind(adress_for_neighbours)
                    info_socket.connect((server, int(self.port_TCP)))
                    request_packet = Packet(PacketType.INFO_REQUEST,int(time.time() * 1000))
                    CTT.send_msg(request_packet, info_socket)
                    #print("-"*20 +"\INFO REQUEST ENVIADO")
                    packet = CTT.recv_msg(info_socket)
                    i = 0
                    while packet == None:
                        #print(i)
                        packet = CTT.recv_msg(info_socket)
                        #i += 1
                    #print(packet)
                    latency = int(packet.data)
                    if latency < best_time:
                        best_time = latency
                        newb_server = server
                    info_socket.close()
                    break
                except Exception as e:
                    #print(f"IN INFO_REQUEST: port {new_port} already in use, trying other...")
                    #time.sleep(2)
                    #print(e)
                    #new_port +=1
                    attempts +=1
                    if attempts >10:
                        break
        #print(best_time)
        return newb_server

                
            
    def best_router(self, list_of_paths):
        #print(f"LISTA DE CAMINHOS A ESCOLHER: {list_of_paths}")
        final_path = list_of_paths[0]
        smallest = len(list_of_paths[0])
        for path in list_of_paths:
            if len(path)<smallest and self.ip in path:
                final_path = path
                smallest = len(path)
        next_router_index = final_path.index(self.ip) + 1
        print(f"CAMINHO ESCOLHIDO PARA ENVIAR VIDEO{final_path}")
        return final_path[next_router_index]