import json
import struct 

def pack_message(data: dict) -> bytes :
    json_str = json.dumps(data) 
    json_bytes = json_str.encode('utf-8')
    length = len(json_bytes)
    length_prefix = struct.pack('>I',length)

    return length_prefix +json_bytes


def recv_exact(sock, num_bytes):
    """keep reading from the socket until we have exact number of num_bytes"""
    data = b''
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk :
            return None
        data += chunk
    return data

def unpack_message(sock):

    length_bytes = recv_exact(sock,4)
    if length_bytes is None:
        return None
    
    length = struct.unpack(">I",length_bytes)[0]

    json_bytes = recv_exact(sock, length)
    if json_bytes is None:
        return None
    
    json_str = json_bytes.decode("utf-8")
    data = json.loads(json_str)
    return data

