from socket import *
import select
from src.core.message_processor import MessageProcessor
from src.core.log_decorator import Log

import logging
from server_config.loger import config_server_log
from src.core.log_decorator import Log

import hmac
import hashlib
import os
import json

from server_config.server_verifier import ServerVerifier
from server_config.db.server_db import DB as ServerDB
from server_config.db.models.messanger_db import User, User_history, Contact_list

from src.core.message_processor import MessageProcessor

SERVER_LOG = logging.getLogger("server")


class Server(metaclass=ServerVerifier):

    BLOCK_LEN: int = 1024
    EOM: bytes = b"ENDOFMESSAGE___"
    ENCODING = "utf-8"

    messanger = MessageProcessor

    server_user = User(
        id=999999,
        name="SERVER",
        password="",
        is_active=True
    )

    _socket = socket(AF_INET, SOCK_STREAM)
    connections = []
    clients = []
    client_host_port = {}
    names = {}

    def __init__(self, host: str, port: int) -> None:
        """
        Инициализация класса Server с настройкой параметров:
            self.host - ip адрес сервера
            self.port - порт сервера
            self.db  - подключение базы данных

            Инициализация сокета
            self._socket.bind((self.host, self.port))
            self._socket.listen(5)
            self._socket.settimeout(0.5)

            Получение доступа к механизму сессий SQLAlchemy
            self.session = self.db.session
        """

        self.host = host
        self.port = port
        self.db = ServerDB()
        self._socket.bind((self.host, self.port))
        self._socket.listen(5)
        self._socket.settimeout(0.5)
        self.session = self.db.session

    def __del__(self):
        self._socket.close()

    @Log(SERVER_LOG)
    def run(self):
        """ Главный метод запуска процесса прослушивания портов """
        while True:
            try:
                client, addr = self._socket.accept()
            except OSError:
                pass
            else:
                print(f'Запрос получен от {str(addr)}')
                SERVER_LOG.debug(f'Запрос получен от {str(addr)}')
                self.identify(client)
                self.server_authenticate(client)
                self.clients.append(client)

            responce_ = []
            write_ = []
            errors_ = []

            try:
                if self.clients:
                    responce_, write_, errors_ = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                SERVER_LOG.error(f'Ошибка работы с сокетами: {err.errno}')
            if responce_:
                for resource in responce_:
                    message = self.get_messages(resource)
                    if message:
                        self.send_message(message)

    def server_authenticate(self, connection):
        """Аутентификация клиента"""
        message = os.urandom(32)
        try:
            connection.send(message)
        except:
            pass
        hash = hmac.new(b'our_secret_key', message, digestmod=hashlib.sha256)
        digest = hash.digest()
        response = connection.recv(len(digest))
        if hmac.compare_digest(digest, response) == False:
            connection.close()

    def identify(self, client):
        """Идентификация клиента"""
        name_password = client.recv(self.BLOCK_LEN)
        name_password = json.loads(name_password.decode('utf-8'))
        client_password = self.session.query(User).filter_by(
            name=name_password['name']).first()

        if client_password is None:
            solt = os.urandom(16)
            hash_password = hashlib.pbkdf2_hmac(
                'sha256', name_password['password'].encode(), solt, 100000)

            hash = solt + hash_password

            client_password = User(password=hash, name=name_password['name'])

            self.session.add(client_password)
            self.session.commit()
            print("Клиент зарегистрирован. Попробуйти залогиниться ещё раз")
            client.close()
            return
        else:
            solt = client_password.password[:16]
            hash_password = hashlib.pbkdf2_hmac(
                'sha256', name_password['password'].encode(), solt, 100000)
            if hash_password != client_password.password[16:]:
                print('Идентификация не пройдена')
                client.close()
                return

        self.client_host_port[name_password['name']] = client

    
    def get_messages(self, source):
        """Получение сообщения от клиента"""
        try:
            data_str = source.recv(self.BLOCK_LEN).decode(self.ENCODING)
            if len(data_str) == 0:
                self.clients.remove(source)
                SERVER_LOG.error(f"Соединение c {source} разорвано")
                return 
            return data_str
        except:
            self.clients.remove(source)
            return SERVER_LOG.error(f"Соединение c {source} разорвано")

    def send_message(self, data_str):
        """Рассылка сообщений"""
        data_obj = json.loads(data_str)
        if data_obj["action"] == "msg":

            if data_obj["to_user"] != "ALL":
                self.send_to_user(data_obj, data_str)
                return
            self.send_to_all(data_str)

    def send_to_user(self, data_obj, data_str):
        """Отправка пользователю"""
        destonation = self.client_host_port.get(data_obj["to_user"], None)

        if not destonation:
            """Сообщение сервера, что пользователя нет в чате"""
            destonation = self.client_host_port[data_obj["from_user"]["name"]]
            no_user_str = MessageProcessor.create_message_to_user(
                from_user=self.server_user,
                to_user=data_obj["from_user"]["name"],
                message=f"Пользователь {data_obj['to_user']} ещё не в чате")
            destonation.send(
                no_user_str.encode_to_json().encode(self.ENCODING))
            return
        try:
            destonation.send(data_str.encode(self.ENCODING))
            return
        except:
            self.clients.remove(destonation)
            return SERVER_LOG.error(f"Соединение c {destonation} разорвано")

    def send_to_all(self, data_str):
        """Отправка всем пользователям"""
        for destonation in self.client_host_port.values():
            try:
                destonation.send(data_str.encode(self.ENCODING))
            except:
                self.clients.remove(destonation)
                return SERVER_LOG.error(f"Соединение c {destonation} разорвано")

    def del_contact(self, nickname, name):
        """Удаление контакта"""
        contact = self.session.query(User).filter_by(name=nickname).first()
        if contact is None:
            answer = json.dumps(
                {'response': 400, 'alert': f'{nickname} not in contacts'})
            return answer

        try:
            del_contact = self.session.query(Contact_list).filter_by(
                contact_id=contact.id).first()
            self.session.delete(del_contact)
            self.session.commit()
            answer = json.dumps(
                {'response': 200, 'alert': f'{nickname} deleted from contacts'})
        except:
            answer = json.dumps(
                {'response': 400, 'alert': f'{nickname} not in your contacts'})

        return answer

    def add_contact(self, nickname, name):
        """Добавление контакта"""
        new_contact = self.session.query(User).filter_by(name=nickname).first()
        if new_contact is None:
            new_contact = User(name=nickname, is_active=False)
            self.session.add(new_contact)
            self.session.commit()
        else:
            checking = self.session.query(Contact_list).filter_by(
                contact_id=new_contact.id).first()
            if checking is None:
                host = self.session.query(User).filter_by(name=name).first()
                contact_for_list = Contact_list(
                    user_id=host.id, contact_id=new_contact.id)
                self.session.add(contact_for_list)
                self.session.commit()
                answer = json.dumps(
                    {'response': 200, 'alert': f'{nickname} add into contacts'})
            else:
                answer = json.dumps(
                    {'response': 400, 'alert': 'Already in contacts'})

        return answer

    def client_contact_list(self, name):
        """Формирует список контактов клиента"""
        try:
            host = self.session.query(User).filter_by(name=name).first()
            client_list = self.session.query(
                Contact_list).filter_by(host_id=host.id).all()
            result = []
            for client in client_list:
                contact = self.session.query(User).filter_by(
                    id=client.contact_id).first()
                if contact is None:
                    break
                result.append(contact.name)
            return result
        except:
            SERVER_LOG.error('DataBase error')

    def client_logout(self, name):
        """Фиксирует выход клиента"""
        try:
            client = self.session.query(User).filter_by(name=name).first()
            client.is_active = False
            print('Session. Changes:', self.session.dirty)
            self.session.commit()

        except:
            self.session.rollback()

    def client_login(self, name, ip):
        """Фиксирует вход клиента"""
        try:
            client = self.session.query(User).filter_by(name=name).first()
            if client is None:
                client = User(name)
                self.session.add(client)

            client.is_active = True
            client_history = User_history(user_id=client.id, ip_address=ip)
            self.session.add(client)
            self.session.add(client_history)

            print('Session. New objects:', self.session.new)
            self.session.commit()

        except:
            return SERVER_LOG.error('Ошибка разговора')


if __name__ == '__main__':

    server = Server(port=8128, ip="localhost")

    server.run()
