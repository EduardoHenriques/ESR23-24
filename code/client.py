import socket, json, time, sys
from utils.packet import *
from client_worker import Client
from tkinter import Tk
CONFIG_PATH = ("Configs/all_hosts.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro - parametros invalidos")
        exit()
    client = sys.argv[1]
    # movie = sys.argv[2]
    # obtain the client and general config info from the file
    root = Tk()
    file = open(CONFIG_PATH,'r') 
    data = json.load(file)
    client = data[client]
    my_name, my_ip, my_router = client["name"],client["ip"], client["router"]
    udp_p,tcp_p,rendezvous_points = client["port_UDP"], client["port_TCP"], data["target_RP"]
    print(udp_p, tcp_p, rendezvous_points)
    file.close()
    nc = Client(my_name, my_ip, my_router, tcp_p, udp_p, root)
    nc.send_Flood_Req("movie.Mjpeg")
    #nc.recv_flood_response()
    nc.send_Media_Req("teste", False)
    root.mainloop()
    #
    


    


