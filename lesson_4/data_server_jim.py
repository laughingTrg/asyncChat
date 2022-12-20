import json
import socket
import sys
from common.utils import get_msg, send_msg
from common.constants import ACTION, TIME, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ALERT, ERROR, MAX_CONNECTIONS, DEFAULT_PORT

def search_msg(msg: dict):
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg \
        and msg[USER][ACCOUNT_NAME] == "Guest":
        return {RESPONSE: 200,
                ALERT: "OK"}
    return {
        RESPONSE: 400,
        ERROR: "Incorrect request"
    }

def create_send_serv_msg(client, msg: dict) -> None:
    correct_send_msg = search_msg(msg)
    send_msg(client, correct_send_msg)

def main():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print(
            'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.bind((listen_address, listen_port))
    connection.listen(MAX_CONNECTIONS)

    while True:

        client, addr = connection.accept()
        try:
            input_msg = get_msg(client)
            print("Сообщение: ", input_msg, ", было отправлено клиентом: ", addr)
            create_send_serv_msg(client, input_msg)
            client.close()
        except(ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
            client.close()

if __name__ == "__main__":
    main()
