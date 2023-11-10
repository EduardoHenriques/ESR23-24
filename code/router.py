import socket
from threading import Thread
import json, sys
from connections import UDPListen, TCPListen
from server_worker import ServerWorker
# Cada router terá o seu código(1,2,...).
# O código vai indicar o ip associado e a sua lista de vizinhos.

CONFIG_PATH = "Configs/all_routers.json"

class Router():
    
    def __init__(self, name, is_rendezvous, ip, port_UDP, port_TCP, neighbours):
        self.name = name 
        self.SW = ServerWorker(name, is_rendezvous, ip, port_UDP, port_TCP, neighbours)
    def __str__(self) -> str:
        return (f"ROUTER: {self.name}")
    
    def run(self):
        print("Start")
        tcp_socket = TCPListen(self.SW)
        udp_socket = UDPListen(self.SW)
        #start threads for each protocol
        tcp_socket.start()
        udp_socket.start()
        #join them (acho que n acontece)
        udp_socket.join()
        tcp_socket.join()



if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Erro - parametros invalidos")
        exit()
    else: 
        args = sys.argv[1:]
        router_name = args[0]
        with open(CONFIG_PATH,'r') as file:
            data = json.load(file)
            r_info = data[router_name]
            r = Router(r_info["name"], r_info["RP"], r_info["ip"], r_info["port_UDP"], r_info["port_TCP"], r_info["neighbours"]) # __init__
            print(r.SW)
            r.run()
    
