from threading import Thread
import json, sys
from connections import UDPListen, TCPListen
# Cada router terá o seu código. O código vai indicar o ip associado e a sua lista de vizinhos.

CONFIG_PATH = "Configs/all_routers.json"

class Router(Thread):
    def __init__(self, name, is_rendezvous, ip, port_UDP, port_TCP, neighbours):
        Thread.__init__(self)
        self.name = name
        self.rendezvous_point = is_rendezvous # Bool
        self.neighbours = neighbours # Array
        self.ip = ip
        self.port_UDP = port_UDP
        self.port_TCP = port_TCP
    
    def __str__(self) -> str:
        return (f"ROUTER: {self.name}\nRP: {self.rendezvous_point}\nIP: {self.ip}\nNEIGHBOURS: {self.neighbours}\nPORT_UDP: {self.port_UDP}\nPORT_TCP: {self.port_TCP}")
    
    def run(self):
        print("Start")
        try:
            ThreadUDP = UDPListen(self.port_UDP, self.ip, "", "") # UDPlisten(PORTA_UDP, IP, servidor, nome)
            ThreadTCP = TCPListen(self.port_TCP, self.ip, "") # TCPListenSP(PORTA, IP, servidor)
            print("Starting Server...")
            ThreadUDP.start()
            ThreadTCP.start()
            print("Server Started!")
            ThreadUDP.join()
            ThreadTCP.join()
        except KeyboardInterrupt:
            print("[SERVER] Servidor interrompido!")
            
if __name__ == "__main__":
    if len(sys.argv) == 0:
        print("Erro - parametros invalidos")
        exit()
    else:
        args = sys.argv[1:]
        router_name = args[0]
        with open(CONFIG_PATH,'r') as file:
            data = json.load(file)
            r_info = data[router_name]
            r = Router(r_info["name"], r_info["RP"], r_info["ip"], r_info["port_UDP"], r_info["port_TCP"], r_info["neighbours"])
            print(r)
            r.run()
    
