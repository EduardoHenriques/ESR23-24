import socket
from connections import TCPListen, UDPListen
from server_worker import ServerWorker
import json, sys

CONFIG_PATH = "Configs/all_servers.json"
FILE_PATH = "movie.Mjpeg"

class Server():
    
    def __init__(self, name, is_rendezvous, ip, port_UDP, port_TCP, neighbours):
        self.name = name 
        self.SW = ServerWorker(name, is_rendezvous, ip, port_UDP, port_TCP, neighbours, "server", "")
        self.tcp_socket = None
    def __str__(self) -> str:
        return (f"ROUTER: {self.name}")
    
    def run(self):
        print("Start")
        self.tcp_socket = TCPListen(self.SW)
        #udp_socket = UDPListen(self.SW)
        #start threads for each protocol
        self.tcp_socket.start()
        #udp_socket.start()
        #join them (acho que n acontece)
        #udp_socket.join()
        #self.tcp_socket.join()



if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Erro - parametros invalidos")
        exit()
    else: 
        args = sys.argv[1:]
        server_name = args[0]
        with open(CONFIG_PATH,'r') as file:
            try:
                data = json.load(file)
                r_info = data[server_name]
                r = Server(r_info["name"], r_info["RP"], r_info["ip"], r_info["port_UDP"], r_info["port_TCP"], r_info["neighbours"]) # __init__
                print(r.SW)
                r.run()
            except KeyboardInterrupt:
                r.tcp_socket.join()
