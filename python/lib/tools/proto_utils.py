
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

def FullMessageToDict(message, without_auth=False):
        if issubclass(type(message), Message):
            return FullMessageToDict(MessageToDict(message), without_auth)
        if isinstance(message, dict):
            if "Auth" in message and without_auth:
                message.pop("Auth")
            return dict(map(lambda x: (x[0], FullMessageToDict(x[1], without_auth)), message.items()))
        if isinstance(message, list):
            return list(map(lambda x : FullMessageToDict(x, without_auth), message))
        return message
