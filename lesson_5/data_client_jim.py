import sys
import json
import socket
import time
import logging
import log.client_log_config
from common.constants import MAX_MSG_BYTES, ENCODING, DEFAULT_IP, DEFAULT_PORT
from common.utils import get_msg, send_msg

client_logger = logging.getLogger('client.main')

def get_client_msg_template() -> dict:
    msg_template = {
        "action": None,
        "time": None,
        "type": None,
        "user": {}
    }
    return msg_template

def send_presence_msg(sock):
    presence_msg = create_presence_msg()
    send_msg(sock, presence_msg)
    client_logger.info('Сформирован запрос на присутствие и отправлен серверу')

def create_presence_msg() -> dict:
    action = "presence"
    timestamp = int(time.time())
    type = "status"
    account_name = "Guest"
    status = "Yep, I'm here"
    presence_msg = get_client_msg_template()
    presence_msg["action"] = action
    presence_msg["time"] = timestamp
    presence_msg["type"] = type
    presence_msg["user"] = {
            "account_name": account_name,
            "status": status,
        }

    return presence_msg

def main():
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP
        server_port = DEFAULT_PORT
    except ValueError:
        client_logger.debug('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((server_address, server_port))
    send_presence_msg(connection)
    try:
        serv_msg = get_msg(connection)
        client_logger.debug(f"Сообщение от сервера: {serv_msg} длинной {len(serv_msg)} байт")
        connection.close()
    except (ValueError, json.JSONDecodeError):
        client_logger.debug('Не удалось декодировать сообщение сервера.')
        connection.close()

if __name__ == "__main__":
    main()