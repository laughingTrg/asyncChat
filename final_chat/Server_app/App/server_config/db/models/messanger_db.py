from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import registry
from datetime import datetime


mapper_register = registry()

user = Table(
    'User',
    mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(24), nullable=False),
    Column('password', String(120), nullable=False),
    Column('is_active', Boolean, default=True),
)
""" Объявление таблицы базы данных пользователя """

user_history = Table(
    'User_history',
    mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey(
        'User.id', ondelete='CASCADE'), nullable=False),
    Column('entry_time', DateTime, default=datetime.utcnow),
    Column('ip_address', String(256), nullable=False)
)
""" Объявление таблицы базы данных истории посещения системы пользователем """

contact_list = Table(
    'Contact_list',
    mapper_register.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey(
        'User.id', ondelete='CASCADE'), nullable=False),
    Column('contact_id', ForeignKey(
        'User.id', ondelete='CASCADE'), nullable=False)
)
""" Объявление таблицы базы данных констактов пользователя """


class User:
    pass


class User_history:
    pass


class Contact_list:
    pass


mapper_register.map_imperatively(User, user)
mapper_register.map_imperatively(Contact_list, contact_list)
mapper_register.map_imperatively(User_history, user_history)
