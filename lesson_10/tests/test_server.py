import unittest
from data_client_jim import get_client_msg_template, create_presence_msg
from data_server_jim import search_msg
from common.constants import ACTION, TIME, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ALERT, ERROR, MAX_CONNECTIONS, DEFAULT_PORT

class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        self.test_msg_template = get_client_msg_template()
        self.test_create_msg_template = create_presence_msg()

    def test_get_responce_200(self):
        """передача соответствующего массива"""
        test_dict = create_presence_msg()
        test_dict["time"] = 100
        self.assertEqual(search_msg(test_dict), {RESPONSE: 200, ALERT: "OK"})

    def test_get_responce_400(self):
        """передача неправильного массива"""
        self.assertEqual(search_msg(self.test_msg_template), {RESPONSE: 400, ERROR: "Incorrect request"})

if __name__ == "__main__":
    unittest.main()