import json
import socket
import sys
import logging
import time
import select
import argparse
import log.server_log_config
from common.utils import get_msg, send_msg
from common.constants import ACTION, TIME, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ALERT, \
    ERROR, MAX_CONNECTIONS, DEFAULT_PORT, MESSAGE_TEXT, SENDER, MESSAGE
from functools import wraps
from wrappers import log

server_logger = logging.getLogger('server.main')

@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        server_logger.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port

@log
def process_client_message(message, messages_list, client):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма.
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    server_logger.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_msg(client, {RESPONSE: 200})
        return
    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    # Иначе отдаём Bad request
    else:
        send_msg(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return

@log
def search_msg(msg: dict):
    server_logger.info('Разбираем полученное сообшение от клиента')
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg \
        and msg[USER][ACCOUNT_NAME] == "Guest":
        server_logger.info(f'Получен корректный статус присутствия пользователя {msg[USER][ACCOUNT_NAME]}')
        return {RESPONSE: 200,
                ALERT: "OK"}
    server_logger.info(f'Получено некорректное сообщение')
    return {
        RESPONSE: 400,
        ERROR: "Incorrect request"
    }

@log
def create_send_serv_msg(client, msg: dict) -> None:
    correct_send_msg = search_msg(msg)
    send_msg(client, correct_send_msg)

def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = arg_parser()

    server_logger.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')

    clients = []
    messages = []

    #устанавливаем подключение
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.bind((listen_address, listen_port))
    connection.settimeout(0.5)
    connection.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, addr = connection.accept()
        except OSError:
            pass
        else:
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_msg(client_with_message),
                                           messages, client_with_message)
                except:
                    server_logger.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_msg(waiting_client, message)
                except:
                    server_logger.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    clients.remove(waiting_client)


if __name__ == "__main__":
    main()
