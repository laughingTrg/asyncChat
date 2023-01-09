import unittest
import json
from data_client_jim import get_client_msg_template, create_presence_msg
from data_server_jim import search_msg
from common.utils import send_msg, get_msg
from common.constants import ACTION, TIME, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ALERT, ERROR, MAX_CONNECTIONS, DEFAULT_PORT, ENCODING, MAX_MSG_BYTES

class TestSocket:

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.receved_message = None

    def send(self, message_to_send):

        json_test_message = json.dumps(self.test_dict)

        self.encoded_message = json_test_message.encode(ENCODING)
        self.receved_message = message_to_send

    def recv(self):

        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)

class Tests(unittest.TestCase):

    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 100.500,
        USER: {
            ACCOUNT_NAME: 'test_Test'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message(self):

        test_socket = TestSocket(self.test_dict_send)
        send_msg(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.receved_message)

    def test_get_message(self):

        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)

        self.assertEqual(get_msg(test_sock_ok), self.test_dict_recv_ok)
        self.assertEqual(get_msg(test_sock_err), self.test_dict_recv_err)

if __name__ == "__main__":
    unittest.main()