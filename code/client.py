import socket, json, time, sys
from utils.packet import *
from client_worker import Client
CONFIG_PATH = ("Configs/all_hosts.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro - parametros invalidos")
        exit()
    client = sys.argv[1]
    # obtain the client and general config info from the file
    file = open(CONFIG_PATH,'r') 
    data = json.load(file)
    client = data[client]
    my_ip, my_router = client["ip"], client["router"]
    udp_p,tcp_p,rendezvous_points = client["port_UDP"], client["port_TCP"], data["target_RP"]
    print(udp_p, tcp_p, rendezvous_points)
    file.close()
    nc = Client(my_ip, "10.0.2.10", 4200, 6969)
    nc.send_Media_Req("asd","10.0.2.10")
    nc.recv_media()


    # connect to router
    # always perform a flooding request...
    #print('-'*25+"\nPERFORMING FLOOD REQUEST...\n"+'-'*25)
    #request_packet = Packet(PacketType.FLOOD_REQUEST,[my_ip])
    #print(request_packet)
    #CTT.send_msg(request_packet, client_socket)
    #time.sleep(3)
    #print(CTT.recv_msg(client_socket))
    # TODO como acabar saber que acabou flood request
    # ..followed by a media request when you get the response back
    #print('-'*25+"\nPERFORMING MEDIA REQUEST...\n"+'-'*25)
    #request_packet = Packet(PacketType.MEDIA_REQUEST,"movie_name")
    #CTT.send_msg(request_packet, client_socket)
    

    # listen for the video frames

