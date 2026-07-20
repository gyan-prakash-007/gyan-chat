import socket 
import threading
from protocol import pack_message, unpack_message

HOST = '127.0.0.1'
PORT = 65432

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))

def receive_messages():
    while True:
        message = unpack_message(client_socket)
        if message is None:
            print('Disconnected from server')
            break
        print(f"\nReceived: {message}")

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start

while True:
    text = input("enter a message")
    data = {"type": "chat", "text":text}
    client_socket.sendall(pack_message(data))