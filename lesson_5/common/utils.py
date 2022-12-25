import json
from common.constants import ENCODING, MAX_MSG_BYTES

def get_msg(client) -> dict:
    raw_serv_msg = client.recv(MAX_MSG_BYTES)
    if isinstance(raw_serv_msg, bytes):
        json_serv_msg = raw_serv_msg.decode(ENCODING)
        serv_msg = json.loads(json_serv_msg)
        if isinstance(serv_msg, dict):
            return serv_msg
        raise ValueError
    raise ValueError

def send_msg(sock, msg):
    json_msg = json.dumps(msg)
    encode_json_msg = json_msg.encode(ENCODING)
    sock.send(encode_json_msg)