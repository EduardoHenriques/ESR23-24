import socket
from server_worker import ServerWorker
from threading import * 
from utils.packet import CTT
import threading

class TCPListen(Thread):

    def __init__(self, sw):
        self.sw = sw
        Thread.__init__(self)

    def run(self):
        try:
            TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # criar socket
            TCP_socket.bind((self.sw.ip, int(self.sw.port_TCP)))  # dar bind ao ip e porta ao servidor
            TCP_socket.listen(5)  # servidor fica à espera de ligaçoes
            while True:
                print(f"[SERVER] Estou à escuta no {self.sw.ip}:{self.sw.port_TCP}")
                client_socket, client_address = TCP_socket.accept()
                print(f"Accepted connection from {client_address}")
                thread = threading.Thread(target=self.sw.process_TCP, args=(client_socket,client_address))
                thread.start()
                
        # funcao para tratar de ligaçoes TCP
        except KeyboardInterrupt:
            print("[SERVER] FIM DO SERVIDOR")
            TCP_socket.close()


class UDPListen(Thread):
    def __init__(self, sw):
        self.sw = sw
        Thread.__init__(self)
        

    def run(self):
        try:
            UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
            UDP_socket.bind((self.sw.ip, int(self.sw.port_UDP)))  # dar bind ao ao ip e porta ao servidor
            print(f"[SERVER] Estou à escuta no {self.sw.ip}:{self.sw.port_UDP}")
            while True:
                data, addr = CTT.recv_msg_udp(UDP_socket)  # Adjust buffer size as needed
                # Process the received data
                thread = threading.Thread(target=self.sw.process_UDP, args=(data, addr))
                thread.start()
                thread.join()
                
        except KeyboardInterrupt:
            print("[SERVER] FIM DO SERVIDOR")

