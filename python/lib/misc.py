
import time
import datetime
from google.protobuf.json_format import ParseDict

def DictToMessage(js_dict, type):
    message = type()
    ParseDict(js_dict, message)
    return message

def datetime_from_timestamp(ts:int):
    return datetime.datetime.fromtimestamp(ts / 1e9)

def get_time_delta(ts:int):
    dt = datetime_from_timestamp(ts)
    return datetime.datetime.now() - dt

def get_timestamp():
    return time.time_ns()
