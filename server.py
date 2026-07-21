import socket
import threading
import time
from protocol import pack_message, unpack_message

HOST = '0.0.0.0'
PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Server listening on {HOST}:{PORT}")


clients = {}
clients_lock = threading.Lock()

PING_INTERVAL = 10
TIMEOUT = 25

def broadcast(message, sender_socket=None):
    data = pack_message(message)
    with clients_lock:
        for client in clients:
            try:
                client.sendall(data)
            except OSError:
                pass


def heartbeat_loop():
    while True :
        time.sleep(PING_INTERVAL)
        now = time.time()
        dead_client = []

        with clients_lock:
            for client_socket, info in clients.items():
                if now - info["last_seen"] > TIMEOUT:
                    dead_client.append(client_socket)
                else :
                    try :
                        client_socket.sendall(pack_message({"type": "ping"}))
                    except OSError:
                        dead_client.append(client_socket)

        for client_socket in dead_client:
            remove_client(client_socket)


def remove_client(client_socket):
    with clients_lock:
        info = clients.pop(client_socket, None)

    if info is None:
        return
    
    client_socket.close()
    print(f"{info["username"]} time out / disconnected")
    broadcast({"type": "system", "text": f"{info['username']} left the chat"})


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
        username_taken = any(info["username"] == username for info in clients.values())

    if username_taken:
        error = {"type": "error", "reason":"username taken"}
        client_socket.sendall(pack_message(error))
        client_socket.close()
        return
        
    with clients_lock:
        clients[client_socket] = {"username" : username , "last_seen": time.time()}

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

        with clients_lock:
            if client_socket in clients:
                clients[client_socket]["last_seen"] = time.time()

        if message.get("type") == "pong":
            continue

        print(f"Received from {client_address}: {message}")
        broadcast(message, sender_socket=client_socket)

    remove_client(client_socket)


threading.Thread(target=heartbeat_loop,daemon = True).start()


while True:
    client_socket , client_address = server_socket.accept()
    print(f"New connection from {client_address}")

    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()