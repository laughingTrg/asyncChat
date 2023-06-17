from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import registry
from datetime import datetime


mapper_register = registry()

user = Table(
    'User', mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String)
)
""" Объявление таблицы базы данных пользователя """

contact_list = Table(
    'Contact_list', mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('host_id', ForeignKey('User.id')),
    Column('contact_id', ForeignKey('User.id')),
)
""" Объявление таблицы базы данных констактов пользователя """

message_history = Table(
    'Message_history', mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('time', String),
    Column('from_', ForeignKey('User.name')),
    Column('to_', ForeignKey('User.name')),
    Column('message', Text),
)
""" Объявление таблицы базы данных истории переписки пользователя """


class User:
    def __repr__(self) -> str:
        return User.name


class Message_history:
    pass


class Contact_list:
    pass


mapper_register.map_imperatively(User, user)
mapper_register.map_imperatively(Contact_list, contact_list)
mapper_register.map_imperatively(Message_history, message_history)
