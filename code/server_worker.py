import socket
import threading
import time
from threading import Thread
import sys, json
import traceback
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
        self.paths = []
    

    def __str__(self) -> str:
        return (f"Server Worker of device {self.device_name}\nPorts(UDP | TCP): {self.port_UDP} | {self.port_TCP}\nRP: {self.RP}\nIPV4: {self.ip}\nNeighbours: {self.neighbours}")

    def send_media(self, addr): 
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
                    packet = Packet(PacketType.MEDIA_RESPONSE, (frameNumber, data))
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
        #TODO receber media_responses e reencaminhar pacotes recebidos
    # Flooding -> Performs flooding on every router except the one that sent the packet
    # Media -> Redirects the media to the host that requested it or to the server
    
    def recv_flood_response(self, n_socket):
        #n_socket.listen()
        print('-' * 10 + "I sleep" + '-' * 10)
        # time.sleep(1)
        #client_socket, client_address = n_socket.accept()
        
        packet = CTT.recv_msg(n_socket)
        print(packet)
        while packet != None:
            if packet.type == PacketType.FLOOD_RESPONSE:
                self.paths.append(packet.data[0])

    def process_TCP(self, client_socket,client_address):
        threads = []
        packet = CTT.recv_msg(client_socket)
        while packet != None:
            print(packet)
            # REQ - FLOOD
            if packet.type == PacketType.FLOOD_REQUEST:
                print(f"flood request from {client_address} to {self.device_name}.")
                data = packet.data
                data[0].append(self.ip) # increase path
                print(self.RP)
                if self.RP == "True":
                    print("pensa que é RP")
                    data[1] = True # has it reached a RP? 
                    packet_response = Packet(PacketType.FLOOD_RESPONSE, data)
                    CTT.send_msg(packet_response, client_socket)
                else:
                    new_request_packet = Packet(PacketType.FLOOD_REQUEST, data)
                    #TODO criar ligações com todos os vizinhos
                    print("enviar request para os vizinhos")
                    new_port = int(self.port_TCP) + 1
                    print(f"Current path: {data[0]}")
                    i = 1
                    for n in self.neighbours:
                        print(f"neighbours:{n}")
                        adress_for_neighbours = (self.ip, new_port)
                        # criar socket
                        neighbours_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        neighbours_socket.bind(adress_for_neighbours)
                        print(f"Connection to{n}, in port {self.port_TCP}")
                        neighbours_socket.connect((n, int(self.port_TCP)))
                        CTT.send_msg(new_request_packet, neighbours_socket)
                        nt = threading.Thread(target=self.recv_flood_response, args=(neighbours_socket,))
                        nt.start()
                        print(f"PACKET {i} SENT")
                        i+=1
                        threads.append(nt)
                        new_port +=1
                    print("enviar resposta de volta")
                    packet_response = Packet(PacketType.FLOOD_RESPONSE, data)
                    CTT.send_msg(packet_response, client_socket)
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
                time.sleep(2)
                self.send_media(client_address)
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

    def end(self):
        self.socket.close()

    #TODO Flood --> Smp q chega ao RP, response com flag de end of the line
    #TODO Routers must know, who they send the Flood Req & When all of them answer(end) you answer(end) 2