from __future__ import print_function

import logging
import sys, os
sys.path.append('./generated')

import grpc
import generated.user_pb2 as user_pb2
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import user_utils


def run():
    print("Making request ... ")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = dating_server_pb2_grpc.DatingServerStub(channel)
        key = user_pb2.TUserKey(Hash=4567890987)
        response = stub.GetUser(dating_server_pb2.UserRequest(Key=key))
    print("Greeter client received: \n" + user_utils.UserToString(response.User))


if __name__ == '__main__':
    logging.basicConfig()
    run()
