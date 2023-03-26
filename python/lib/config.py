import sys, os
import generated.config_pb2 as config_pb2
from google.protobuf import text_format

# sys.path.append('./generated')
# dir_path =

def read_config_from(config_class, config_path):
    with open(config_path, 'r+') as file:
        config = config_class()
        text_format.Parse(''.join(file.readlines()), config)
        return config

def read_configs(path=os.path.dirname(__file__) + "/../private_data.txt.pb"):
    with open(path, 'r+') as file:
        config = config_pb2.TPrivateData()
        text_format.Parse(''.join(file.readlines()), config)
        return config



# read_configs()


