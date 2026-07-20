import socket
import threading
from protocol import pack_message, unpack_message

HOST = '127.0.0.1'
PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Server listening on {HOST}:{PORT}")

clients = {}
clients_lock = threading.Lock()


def broadcast(message, sender_socket=None):
    data = pack_message(message)
    with clients_lock:
        for client in clients:
            try:
                client.sendall(data)
            except OSError:
                pass


def handle_client(client_socket, client_address):
    print(f"Handling client {client_address}")

    # ---HANDSHAKE (unique username allocation)---
    try :
        join_message = unpack_message(client_socket)
    except OSError:
        client_socket.close()
        return
    
    if join_message is None or join_message.get("type") != "join" :
        client_socket.close()
        return
    
    username = join_message.get("username")

    with clients_lock:
        username_taken = username in clients.values()

    if username_taken:
        error = {"type": "error", "reason":"username taken"}
        client_socket.sendall(pack_message(error))
        client_socket.close()
        return
        
    with clients_lock:
        clients[client_socket] = username

    ack = {"type": "join_ack", "status": "ok"}
    client_socket.sendall(pack_message(ack))

    broadcast({"type" : "system", "text": f"{username} joined the chat"})
    print(f"{username} joined")

    while True:
        try :
            message = unpack_message(client_socket)
        except OSError:
            break

        if message is None:
            break

        print(f"Received from {client_address}: {message}")
        broadcast(message, sender_socket=client_socket)

    with clients_lock:
        if client_socket in clients:
            del clients[client_socket]

    client_socket.close()
    broadcast({"type": "system", "text": f"{username} left the chat"})
    print(f"{username} disconnected")



while True:
    client_socket , client_address = server_socket.accept()
    print(f"New connection from {client_address}")

    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()