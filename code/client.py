import socket, json, time, sys
from utils.packet import *
from connections import TCPListen, UDPListen
from server_worker import ServerWorker

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
    udp_p,tcp_p,rendezvous_points = data["port_UDP"], data["port_TCP"], data["target_RP"]
    file.close()
    
    # create server worker, with 2 threads to listen to each type of connnection
    sw = ServerWorker("client",False,my_ip,udp_p,tcp_p,[my_router],"host")
    print(sw)
    tcp_listen, udp_listen = TCPListen(sw), UDPListen(sw)
    tcp_listen.run()
    udp_listen.run()
    # always perform a flooding request...
    print('-'*25+"\nPERFORMING FLOOD REQUEST...\n"+'-'*25)
    request_packet = Packet(PacketType.FLOOD_REQUEST,"?????")
    CTT.send_msg(request_packet, sw.port_TCP)
    # ..followed by a media request when you get the response back
    print('-'*25+"\nPERFORMING MEDIA REQUEST...\n"+'-'*25)
    
