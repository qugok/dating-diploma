import sys, os
import generated.config_pb2 as config_pb2
from google.protobuf import text_format

sys.path.append('/home/alex/mipt/1c/diploma2/hello/dating-diploma/python/generated')

def read_configs(path="../private_data.txt.pb"):
    with open(path, 'r+') as file:
        config = config_pb2.TPrivateData()
        text_format.Parse(''.join(file.readlines()), config)
        return config



# read_configs()


