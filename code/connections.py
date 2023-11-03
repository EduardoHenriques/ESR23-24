import socket
from threading import Thread
import pickle

class TCPListen(Thread):

    def __init__(self, porta, ip, servidor):
        self.porta = int(porta)
        self.ip = ip
        self.type = "TCP"
        self.servidor = servidor

        Thread.__init__(self)

    def run(self):
        try:
            TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # criar socket
            TCP_socket.bind((self.ip, self.porta))  # dar bind ao ip e porta ao servidor
            TCP_socket.listen(5)  # servidor fica à espera de ligaçoes
            print(f"[SERVER] Estou à escuta no {self.ip}:{self.porta}")
            while True:
                # Accept an incoming connection
                client_socket, client_address = TCP_socket.accept()
                print(f"Accepted connection from {client_address}")

                # Receive data from the client
                data = client_socket.recv(1024)  # Adjust buffer size as needed

                if not data:
                    break  # Exit the loop if the client disconnects

                # Process the received data
                print(f"Received data from {client_address}: {data.decode('utf-8')}")

                # You can send a response to the client here if needed

                # Close the client socket
                client_socket.close()
        # funcao para tratar de ligaçoes TCP
        except KeyboardInterrupt:
            print("[SERVER] FIM DO SERVIDOR")


class UDPListen(Thread):
    def __init__(self, porta, ip, servidor, nomeServer):
        self.porta = int(porta)
        self.ip = ip
        self.type = "UDP"
        self.servidor = servidor
        self.nomeServer = nomeServer
        Thread.__init__(self)
        

    def run(self):
        try:
            UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # criar socket UDP
            UDP_socket.bind((self.ip, self.porta))  # dar bind ao ao ip e porta ao servidor
            print(f"[SERVER] Estou à escuta no {self.ip}:{self.porta}")
            while True:
                data, addr = UDP_socket.recvfrom(1024)  # Adjust buffer size as needed
                # Process the received data
                print(f"Received data from {addr}: {data.decode('utf-8')}")
                
        except KeyboardInterrupt:
            print("[SERVER] FIM DO SERVIDOR")
            
@staticmethod
def serialize(msg):
    return pickle.dumps(msg)

@staticmethod
def deserialize(msg_bytes):
    try:
        data = pickle.loads(msg_bytes)
    except EOFError:
        data = 'null'  # or whatever you want
