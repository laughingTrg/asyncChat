from sqlalchemy import Integer, String, Column, ForeignKey, create_engine, Table, MetaData, text, select as sel, delete
from sqlalchemy.orm import declarative_base, Mapped, relationship, session, Session

Base = declarative_base()

class ClientDB(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    login = Column(String)
    info = Column(String)

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return "<CLient('%s', '%s')>" % (self.login, self.info)

class ClientHistoryDB(Base):
    __tablename__ = "client_history"

    id = Column(Integer, primary_key=True)
    login_time = Column(String)
    ip_addr = Column(String)

    def __init__(self, login_time, ip_addr):
        self.login_time = login_time
        self.ip_addr = ip_addr

    def __repr__(self):
        return "<CLientHistory('%s', '%s')>" % (self.login_time, self.ip_addr)

class ClientContactListDB(Base):
    __tablename__ = "contact_list"

    id = Column(Integer, primary_key=True)
    id_owner = Column(ForeignKey("client.id"), nullable=False)
    id_client = Column(ForeignKey("client.id"), nullable=False)

    def __init__(self, id_owner, id_client):
        self.id_owner = id_owner
        self.id_client = id_client

    def __repr__(self):
        return "<CLientContacts('%s', '%s')>" % (self.id_owner, self.id_client)

class Storage():

    def __init__(self, engine):
        self.engine = create_engine(engine, echo=False)
        metadata = Base.metadata
        metadata.create_all(self.engine)

    def check_user_name(self, user_name: str):
        with Session(self.engine) as session:
            with session.begin():
                statement = sel(ClientDB.id).filter_by(login=user_name)
                result = session.execute(statement).all()
                return result

    def get_contacts_list(self, user_owner_name):
        user_id = self.get_user_id(user_owner_name)
        with Session(self.engine) as session:
            with session.begin():
                statement = sel(ClientDB.login).join(ClientContactListDB, ClientDB.id == ClientContactListDB.id_client)\
                    .filter(ClientContactListDB.id_owner == user_id)
                result = session.scalars(statement).all()
                return result

    def get_all_clients(self):
        with Session(self.engine) as session:
            with session.begin():
                statement = sel(ClientDB.login)
                result = session.execute(statement).all()
                return result

    def get_user_id(self, user_login: str):
        with Session(self.engine) as session:
            with session.begin():
                statement = sel(ClientDB.id).filter_by(login=user_login)
                try:
                    result = session.scalars(statement).one()
                except:
                    result = None
                return result

    def add_user(self, login, info=''):
        with Session(self.engine) as session:
            with session.begin():
                new_client = ClientDB(login, info)
                session.add(new_client)
                session.commit()

    def add_contact(self, username_owner, username_client):
        owner_id = self.get_user_id(username_owner)
        client_id = self.get_user_id(username_client)
        with Session(self.engine) as session:
            with session.begin():
                add_contact = ClientContactListDB(owner_id, client_id)
                session.add(add_contact)
                session.commit()

    def del_contact(self, username_owner, username_client):
        owner_id = self.get_user_id(username_owner)
        client_id = self.get_user_id(username_client)
        with Session(self.engine) as session:
            with session.begin():
                contact = sel(ClientContactListDB).filter(ClientContactListDB.id_owner == owner_id,
                                                          ClientContactListDB.id_client == client_id)
                session.delete(contact)
                session.commit()

    def check_contact(self, username_owner, username_client):
        owner_id = self.get_user_id(username_owner)
        client_id = self.get_user_id(username_client)
        with Session(self.engine) as session:
            with session.begin():
                stmnt = sel(ClientContactListDB.id_client).filter(ClientContactListDB.id_owner == owner_id,
                                                                  ClientContactListDB.id_client == client_id)
                if session.scalars(stmnt).first() is None:
                    return False
                return True