import socket
import time
user_input = input("Enter something: ")
if user_input == "1":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "10.0.0.1"
    server_port = 4200 # UDP
    #try
    client_socket.connect((server_ip, server_port))
    i = 1
    while i <= 10:
        message = f"PACOTE Teste {i}"
        client_socket.send(message.encode('utf-8'))
        print("PACKET ENVIADO")
        i +=1
        time.sleep(3)
    message = "last"
    client_socket.send(message.encode('utf-8'))
    client_socket.close()
else:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "10.0.0.1"
    server_port = 6969 # UDP
    client_socket.connect((server_ip, server_port))
    i = 1
    while i <= 10:
        message = f"DATAGRAM Teste {i}"
        client_socket.send(message.encode('utf-8'))
        print("DATAGRAM ENVIADO")
        i +=1
        time.sleep(3)
    message = "last"
    client_socket.send(message.encode('utf-8'))
    client_socket.close()
