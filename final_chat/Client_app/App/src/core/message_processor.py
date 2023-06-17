import json
import datetime
from typing import Any


class MessageProcessorEncoder(json.JSONEncoder):
    def default(self, obj) -> Any:
        return obj.__dict__


class MessageProcessor():

    def __init__(self, message) -> None:
        for key, val in message.items():
            if isinstance(val, dict):
                sub_val = MessageProcessor(val)
                setattr(self, key, sub_val)
            else:
                setattr(self, key, val)

    def encode_to_json(self):
        return MessageProcessorEncoder().encode(self)

    @staticmethod
    def _gen_default_message(from_user, action):
        return {
            "action": action,
            "time": str(datetime.datetime.now().replace(microsecond=0)),
            "from_user": {
                "id": from_user.id,
                "name": from_user.name,
                "status": "here",
            }
        }

    @staticmethod
    def get_object_from_json(json_obj):
        return json.JSONDecoder(object_hook=MessageProcessor).decode(json_obj)

    @staticmethod
    def create_presence_message(from_user, _action: str = "presence"):
        genered_message = MessageProcessor._gen_default_message(from_user=from_user, action=_action)
        return MessageProcessor(genered_message)

    @staticmethod
    def create_message_to_user(from_user, to_user, message, _action: str = "msg"):
        genered_message = MessageProcessor._gen_default_message(from_user, action=_action)
        genered_message['to_user'] = to_user
        genered_message['message'] = message
        return MessageProcessor(genered_message)

    @staticmethod
    def create_message_to_chat(from_user, message, _action: str = "msg"):
        genered_message = MessageProcessor._gen_default_message(from_user, action=_action)
        genered_message["to_user"] = "ALL"
        genered_message["message"] = message
        return MessageProcessor(genered_message)

    @staticmethod
    def join_chat(from_user, room_name, _action: str = "join"):
        genered_message = MessageProcessor._gen_default_message(from_user, action=_action)
        genered_message["room"] = room_name
        return MessageProcessor(genered_message)

    @staticmethod
    def leave_chat(from_user, room_name, _action: str = "leave"):
        genered_message = MessageProcessor._gen_default_message(from_user, action=_action)
        genered_message["room"] = room_name
        return MessageProcessor(genered_message)

    @staticmethod
    def create_response_message(code, alert=None):
        return MessageProcessor({'response': code, 'alert': alert})

    @staticmethod
    def get_contact_list(from_user, _action: str = "get_contacts"):
        return MessageProcessor._gen_default_message(from_user, action=_action)

    @staticmethod
    def add_contact(from_user, user_id, _action: str = "add_contact"):
        genered_message = MessageProcessor._gen_default_message(from_user, action=_action)
        genered_message["user_id"] = user_id
        return MessageProcessor(genered_message)

    @staticmethod
    def dell_contact(from_user, user_id, _action: str = "del_contact"):
        genered_message = MessageProcessor._gen_default_message(from_user, action=_action)
        genered_message["user_id"] = user_id
        return MessageProcessor(genered_message)
