import threading
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QTableWidgetItem, qApp
from sqlalchemy import Integer, String, Column, ForeignKey, create_engine, Table, MetaData, \
    text, select, delete
from sqlalchemy.orm import declarative_base, Mapped, relationship, session, Session
from PyQt5 import QtWidgets
import sys
import json
import socket
import sys
import logging
import time
import select
import argparse
from sqlalchemy import Integer, String, Column, ForeignKey, create_engine, Table, MetaData, text, select as sel, delete
from sqlalchemy.orm import declarative_base, Mapped, relationship, session, Session
import log.server_log_config
from common.utils import get_msg, send_msg
from common.constants import ACTION, TIME, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ALERT, \
    ERROR, MAX_CONNECTIONS, DEFAULT_PORT, MESSAGE_TEXT, SENDER, MESSAGE, RESPONSE_200, \
    RESPONSE_400, DESTINATION, EXIT, GET_CONTACTS, USER_LOGIN, RESPONSE_202, DB_ENGINE, ADD_CONTACT, DEL_CONTACT, USER_ID
from functools import wraps
from wrappers import log
from metaclasses import ServerMaker
from descriptors import Port
from serv_database_conf import Storage
from serv_form_conf import mywindow

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

class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port

        self.database = database

        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()

        # Конструктор предка
        super().__init__()

    def set_gui_params(self, adr, port):
        try:
            port = int(port)
        except ValueError:
            server_logger.debug('Неправильно указан порт в gui, порт должен быть числом')
        else:
            if self.addr != adr:
                self.addr = adr
            if self.port != port:
                self.port = port


    def init_socket(self):
        server_logger.info(
            f'Запущен сервер, порт для подключений: {self.port} , '
            f'адрес с которого принимаются подключения: {self.addr}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.bind((self.addr, self.port))
        connection.settimeout(0.5)

        # Начинаем слушать сокет.
        self.sock = connection
        self.sock.listen()

    def run(self):
        # Инициализация Сокета
        self.init_socket()

        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                server_logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_msg(client_with_message), client_with_message)
                    except:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    server_logger.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    # Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение, список зарегистрированых
    # пользователей и слушающие сокеты. Ничего не возвращает.

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_msg(self.names[message[DESTINATION]], message)
            server_logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    # Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента, проверяет корректность, отправляет
    #     словарь-ответ в случае необходимости.
    def process_client_message(self, message, client):
        server_logger.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            # Если такого пользователя ещё нет в базе данных, добавляем его.
            if len(self.database.check_user_name(message[USER][ACCOUNT_NAME])) < 1:
                self.database.add_user(str(message[USER][ACCOUNT_NAME]))
                server_logger.debug(f'Новый пользователь: {message[USER][ACCOUNT_NAME]} добавлен в базу данных')
            # Если такой пользователь ещё не зарегистрирован, регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_msg(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_msg(client, response)
                self.clients.remove(client)
                client.close()
            return

        # Если это запрос списка контактов, принимаем и отвечаем
        elif ACTION in message and message[ACTION] == GET_CONTACTS and TIME in message and USER_LOGIN in message:
            # Если пользователь зарегистрирован получаем его id и отправляем список пользователей,
            # иначе отправляем ответ и завершаем соединение.
            print('user_id:', self.database.get_user_id(message[USER_LOGIN]))
            if self.database.get_user_id(message[USER_LOGIN]) is None:
                response = RESPONSE_400
                response[ERROR] = 'Данного пользователя не существует'
                send_msg(client, response)
                self.clients.remove(client)
                client.close()
            else:
                contact_list = self.database.get_contacts_list(message[USER_LOGIN])
                response = RESPONSE_202
                response[ALERT] = contact_list
                send_msg(client, response)

        # Если это запрос на добавление или удаление контакта
        elif ACTION in message and (message[ACTION] == ADD_CONTACT or message[ACTION] == DEL_CONTACT) and TIME in message \
                and USER_ID in message and USER_LOGIN in message:
            if message[ACTION] == ADD_CONTACT:
                if not self.database.check_contact(message[USER_LOGIN], message[USER_ID]):
                    self.database.add_contact(message[USER_LOGIN], message[USER_ID])
                    response = RESPONSE_200
                    send_msg(client, response)
                    return
                else:
                    response = RESPONSE_400
                    response[ERROR] = 'Такой контакт уже существует'
                    send_msg(client, response)
                    return
            else:
                if self.database.check_contact(message[USER_LOGIN], message[USER_ID]):
                    self.database.del_contact(message[USER_LOGIN], message[USER_ID])
                    response = RESPONSE_200
                    send_msg(client, response)
                    return
                else:
                    response = RESPONSE_400
                    response[ERROR] = 'Такого контакта в списке не существует'
                    send_msg(client, response)
                    return



        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_msg(client, response)
            return

def main():
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    listen_address, listen_port = arg_parser()

    # Подключаемся к БД
    db = Storage(DB_ENGINE)

    # Создание экземпляра класса - сервера.
    server = Server(listen_address, listen_port, db)
    server.daemon =True

    app = QtWidgets.QApplication([])
    application = mywindow(db, server)

    timer = QTimer()
    timer.timeout.connect(application.fill_table)
    timer.start(1000)

    # server.main_loop()
    application.show()
    app.exec_()
    # sys.exit(app.exec())


if __name__ == '__main__':
    main()

