import unittest
from data_client_jim import get_client_msg_template, create_presence_msg

class TestClass(unittest.TestCase):

    def setUp(self) -> None:
        self.test_msg_template = get_client_msg_template()
        self.test_create_msg_template = create_presence_msg()

    def test_get_msg_template(self):
        test = get_client_msg_template()
        self.assertEqual(test, {"action": None, "time": None, "type": None, "user": {}})

    def test_create_presence_msg(self):
        self.test_create_msg_template["time"] = 100
        self.assertEqual(self.test_create_msg_template, {"action": "presence", "time": 100, "type": "status",
                                         "user": {"account_name": "Guest", "status": "Yep, I'm here"}})

if __name__ == "__main__":
    unittest.main()