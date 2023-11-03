import socket
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = "10.0.0.1"
server_port = 4200 # UDP

client_socket.connect((server_ip, server_port))
i = 1
while i <= 5:
    message = f"Datagrama Teste {i}"
    client_socket.send(message.encode('utf-8'))
    print("PACKET ENVIADO")
    i +=1
    time.sleep(3)
client_socket.close()