import sys
import json
import socket
import time
import logging
import argparse
import threading
import log.client_log_config
from sqlalchemy import Integer, String, Column, ForeignKey, create_engine, Table, MetaData, text, select as sel, delete
from sqlalchemy.orm import declarative_base, Mapped, relationship, session, Session
import log.server_log_config
from common.constants import ACTION, ENCODING, DEFAULT_IP, DEFAULT_PORT, ERROR, MESSAGE_TEXT, MESSAGE, \
    SENDER, TIME, ACCOUNT_NAME, RESPONSE, DESTINATION, EXIT, PRESENCE, USER, GET_CONTACTS, USER_LOGIN, \
    ALERT, ADD_CONTACT, DEL_CONTACT, USER_ID, CLIENT_DB_ENGINE
from common.utils import get_msg, send_msg
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from wrappers import log
from metaclasses import ClientMaker

client_logger = logging.getLogger('client.main')

Base = declarative_base()

# Классы для описания таблиц в базе данных
class ClientMessageHistoryDB(Base):
    __tablename__ = "client_history"

    id = Column(Integer, primary_key=True)
    name_owner = Column(String)
    name_client = Column(String)
    message = Column(String)

    def __init__(self, name_owner, name_client, message):
        self.name_owner = name_owner
        self.name_client = name_client
        self.message = message

    def __repr__(self):
        return "<ClientMessageHistory('%s', '%s', '%s')>" % (self.name_owner, self.name_client, self.message)

class ClientContactListDB(Base):
    __tablename__ = "contact_list"

    id = Column(Integer, primary_key=True)
    name_owner = Column(String)
    name_client = Column(String)

    def __init__(self, name_owner, name_client):
        self.name_owner = name_owner
        self.name_client = name_client

    def __repr__(self):
        return "<CLientContacts('%s', '%s')>" % (self.name_owner, self.name_owner)

class Storage():

    def __init__(self, engine):
        self.engine = create_engine(engine)
        metadata = Base.metadata
        metadata.create_all(self.engine)

    def add_contact(self, name_owner, name_client):
        if not self.check_contact(name_owner, name_client):
            with Session(self.engine) as session:
                with session.begin():
                    new_client = ClientContactListDB(name_owner, name_client)
                    session.add(new_client)
                    session.commit()
                    client_logger.debug(f'Клиент {name_client} добавлен в список контактов')
        else:
            print('Такой контакт уже существует в списке контактов')

    def del_contact(self, name_owner, name_client):
        if self.check_contact(name_owner, name_client):
            with Session(self.engine) as session:
                with session.begin():
                    old_client = sel(ClientContactListDB).filter(ClientContactListDB.name_owner == name_owner,
                                                                  ClientContactListDB.name_client == name_client)
                    session.delete(old_client)
                    session.commit()
                    client_logger.debug(f'Клиент {name_client} удален из списка контактов')
        else:
            print('Такого контакта в списке контактов не существует')

    def check_contact(self, username_owner, username_client) -> bool:
        with Session(self.engine) as session:
            with session.begin():
                stmnt = sel(ClientContactListDB.name_client).filter(ClientContactListDB.name_owner == username_owner,
                                                                  ClientContactListDB.name_client == username_client)
                if session.scalars(stmnt).first() is None:
                    return False
                return True

    def save_message(self, name_from, name_to, message):
        if self.check_contact(name_from, name_to):
            with Session(self.engine) as session:
                with session.begin():
                    new_message = ClientMessageHistoryDB(name_from, name_to, message)
                    session.add(new_message)
                    session.commit()
                    client_logger.debug(f'Сохраняем сообщение {message} от {name_from} для {name_to}')
        else:
            print(f"Пользователи {name_from}, {name_to} не могут общаться потому, что не добавлены в список контактов")

# Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем.
class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Функция создаёт словарь с сообщением о выходе.
    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

        # Функция запрашивает кому отправить сообщение и само сообщение, и отправляет полученные данные на сервер.

    def create_message(self):
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_msg(self.sock, message_dict)
            client_logger.info(f'Отправлено сообщение для пользователя {to}')

        except:
            client_logger.critical('Потеряно соединение с сервером.')
            exit(1)

    def add_contact(self, nickname):
        message_dict = {
                ACTION: ADD_CONTACT,
                USER_ID: nickname,
                TIME: time.time(),
                USER_LOGIN: self.account_name
            }
        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_msg(self.sock, message_dict)
            client_logger.info(f'Отправлен запрос на добавление в список контактов пользователя {nickname}')
            db.add_contact(self.account_name, nickname)
        except:
            client_logger.critical('Потеряно соединение с сервером.')
            exit(1)

    def del_contact(self, nickname):
        message_dict = {
                ACTION: DEL_CONTACT,
                USER_ID: nickname,
                TIME: time.time(),
                USER_LOGIN: self.account_name
            }
        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_msg(self.sock, message_dict)
            client_logger.info(f'Отправлен запрос на удаление из списка контактов пользователя {nickname}')
            db.del_contact(self.account_name, nickname)
        except:
            client_logger.critical('Потеряно соединение с сервером.')
            exit(1)

    # Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения
    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'add_contact':
                contact_name = input('Введите имя котакта: ')
                self.add_contact(contact_name)
            elif command == 'add_contact':
                contact_name = input('Введите имя котакта: ')
                self.del_contact(contact_name)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_msg(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения.')
                client_logger.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    # Функция выводящяя справку по использованию.
    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('add_contact - добавить контакт в список контактов')
        print('del_contact - удалить контакт из списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

# Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль.
class ClientReader(threading.Thread , metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль. Завершается при потере соединения.
    def run(self):
        while True:
            try:
                message = get_msg(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    client_logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    db.save_message(message[SENDER], message[DESTINATION], message[MESSAGE_TEXT])
                elif RESPONSE in message:
                    client_logger.debug(f'Получен ответ от сервера {message}')
                else:
                    client_logger.error(f'Получено некорректное сообщение с сервера: {message}')

            except IncorrectDataRecivedError:
                client_logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                client_logger.critical(f'Потеряно соединение с сервером.')
                break

# Функция генерирует запрос о присутствии клиента
@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    client_logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


# Функция разбирает ответ сервера на сообщение о присутствии, возращает 200 если все ОК или генерирует исключение при\
# ошибке.
@log
def process_response_ans(message):
    client_logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)

@log
def get_contacts(sock, account_name):
    message_dict = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER_LOGIN: account_name
    }
    client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_msg(sock, message_dict)
        client_logger.info(f'Отправлен запрос списка контактов пользователя {account_name}')
    except:
        client_logger.critical('Потеряно соединение с сервером.')
        exit(1)

@log
def get_response_with_contacts(message):
    client_logger.debug(f'Разбор сообщения о списке контактов от сервера: {message}')
    if RESPONSE in message and ALERT in message:
        if message[RESPONSE] == 202:
            return message[ALERT]
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ALERT]}')
    raise ReqFieldMissingError(RESPONSE)

# Парсер аргументов коммандной строки
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        client_logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name

def main():
    # Сообщаем о запуске
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    # Список контактов
    contacts = []

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    client_logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((server_address, server_port))
        send_msg(connection, create_presence(client_name))
        answer = process_response_ans(get_msg(connection))
        client_logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')

        # получение списка контактов
        get_contacts(connection, client_name)
        contacts = get_response_with_contacts(get_msg(connection))
        print('Контакты клиента:', contacts)
    except json.JSONDecodeError:
        client_logger.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        client_logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        client_logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        client_logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        # Если соединение с сервером установлено корректно, запускаем клиенский процесс приёма сообщний
        module_reciver = ClientReader(client_name, connection)
        module_reciver.daemon = True
        module_reciver.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем.
        module_sender = ClientSender(client_name, connection)
        module_sender.daemon = True
        module_sender.start()
        client_logger.debug('Запущены процессы')

        # Watchdog оснокововной цикл, если один из пот завершён, то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if module_reciver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    db = Storage(CLIENT_DB_ENGINE)
    main()