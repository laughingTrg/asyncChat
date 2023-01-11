
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

# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}