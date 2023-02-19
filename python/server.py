from concurrent import futures
import logging

import sys, os
sys.path.append('/home/alex/mipt/1c/diploma2/hello/dating-diploma/python/generated')

import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import user_utils
import base_client

class DatingServer(dating_server_pb2_grpc.DatingServerServicer):

    def GetUser(self, request, context):
        print("Got Request with Key :", user_utils.KeyToString(request.Key))
        return dating_server_pb2.UserReply(User=base_client.read_user(request.Key))

    def SetUser(self, request, context):
        try :
            base_client.insert_user(request.User)
        except Exception as e:
            print("SetUser: got exception ::", e)
            return dating_server_pb2.SetUserReply(ErrorMessage=str(e))
        return dating_server_pb2.SetUserReply(User=base_client.read_user(request.User.Key))


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dating_server_pb2_grpc.add_DatingServerServicer_to_server(DatingServer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
