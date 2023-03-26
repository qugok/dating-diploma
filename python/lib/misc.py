

from google.protobuf.json_format import ParseDict

def DictToMessage(js_dict, type):
    message = type()
    ParseDict(js_dict, message)
    return message
