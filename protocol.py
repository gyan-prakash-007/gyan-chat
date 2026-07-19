import json
import struct 

def pack_message(data: dict) -> bytes :
    json_str = json.dump(data) 
    json_bytes = json_str.encode('utf-8')
    length = len(json_bytes)
    length_prefix = struct.pack('>I',length)

    return length_prefix +json_bytes