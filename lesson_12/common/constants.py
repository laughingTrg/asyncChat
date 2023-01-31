
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 7777
MAX_MSG_BYTES = 1024
ENCODING = "utf-8"
MAX_CONNECTIONS = 5

ACTION = "action"
TIME = "time"
PRESENCE = "presence"
RESPONSE = "response"
ERROR = "error"
USER = "user"
ACCOUNT_NAME = "account_name"
ALERT = "alert"

MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
SENDER = 'from'
DESTINATION = 'to'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
GET_CONTACTS = 'get_contacts'
USER_ID = 'user_id'
USER_LOGIN = 'user_login'

DB_ENGINE = 'sqlite:///db.sqlite3'
CLIENT_DB_ENGINE = 'sqlite:///db_client.sqlite3'

# 200
RESPONSE_200 = {RESPONSE: 200}

# 202
RESPONSE_202 = {
    RESPONSE: 202,
    ALERT: None
}

# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}