import socket
from server_worker import ServerWorker
from threading import * 
import pickle, threading

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
                # Receive data from the client
                #data = client_socket.recv(1024)  # Adjust buffer size as needed
                #if not data:
                    #break  # Exit the loop if the client disconnects

                # Process the received data
                #print(f"Received data from {client_address}: {data.decode('utf-8')}")

                # You can send a response to the client here if needed

                # Close the client socket
                #client_socket.close()
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
                data, addr = UDP_socket.recvfrom(1024)  # Adjust buffer size as needed
                # Process the received data
                thread = threading.Thread(target=self.sw.process_UDP, args=(data, addr))
                thread.start()
                thread.join()
                
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
