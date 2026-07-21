import socket 
import threading
from protocol import pack_message, unpack_message

HOST = '127.0.0.1'
PORT = 65432

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))

username = input("\nChoose a Username: ")
client_socket.sendall(pack_message({"type":"join", "username": username}))

response = unpack_message(client_socket)

if response is None:
    print("server closed the connection")
    exit()

if response.get("type") == "error":
    print(f"Could not join : {response.get('reason')}")
    client_socket.close()
    exit()

print("Connected as", username)
def receive_messages():
    while True:
        try :
            message = unpack_message(client_socket)
        except OSError:
            break
        if message is None:
            print('\nDisconnected from server')
            break

        if message.get("type") == "ping":
            client_socket.sendall(pack_message({"type": "pong"}))
            continue
        
        msg_type = message.get("type")
        
        if msg_type == "chat":
            print(f"\n{message.get('from', 'unknown')}: {message.get('text')}")
        elif msg_type == "system":
             print(f"\n*** {message.get('text')} ***")
        elif msg_type == "error":
            print(f"\nError: {message.get('reason')}")
        else :
            print(f"\nReceived: {message}")

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

while True:
    text = input("enter a message : ")
    if text.strip() == "/bye":
        print("Leaving the chat...")
        client_socket.close()
        break
    data = {"type": "chat", "text":text}
    client_socket.sendall(pack_message(data))