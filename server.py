import socket
import threading
from protocol import pack_message, unpack_message

HOST = '127.0.0.1'
PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Server listening on {HOST}:{PORT}")

def handle_client(client_socket, client_address):
    print(f"Handling client {client_address}")

    while True:
        message = unpack_message(client_socket)
        if message is None:
            print(f"{client_address} disconnected")
            client_socket.close()
            break
        print(f"Received from {client_address}: {message}")


while True:
    client_socket , client_address = server_socket.accept()
    print(f"New connection from {client_address}")

    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()