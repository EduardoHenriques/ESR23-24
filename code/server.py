import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "10.0.0.1"
UDP_port = 1223
server_socket.bind((host, UDP_port))

server_socket.listen(5)

print(f"A ouvir em {host}:{UDP_port}")

client_socket, client_address = server_socket.accept()
print(f"Ligação de {client_address}")

packets = 0

while True:
    data = client_socket.recv(1024)
    if not data:
        break
    print(f"Recebeu: {data.decode('utf-8')}")
    packets +=1
    if packets == 5:
        break

client_socket.close()
server_socket.close()
