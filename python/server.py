from concurrent import futures
import logging

import sys, os
sys.path.append('./generated')

import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import user_utils
from base_client import CouchbaseClient

class DatingServer(dating_server_pb2_grpc.DatingServerServicer):

    def __init__(self):
        super().__init__()
        self.BDClient = CouchbaseClient()

    def GetUser(self, request, context):
        print("Got Request with Key :", user_utils.KeyToString(request.Key))
        return dating_server_pb2.UserReply(User=self.BDClient.read_user(request.Key))

    def SetUser(self, request, context):
        try :
            self.BDClient.insert_user(request.User)
        except Exception as e:
            print("SetUser: got exception ::", e)
            return dating_server_pb2.SetUserReply(ErrorMessage=str(e))
        return dating_server_pb2.SetUserReply(User=self.BDClient.read_user(request.User.Key))

    def SearchAllNeighbours(self, request, context):
        try :
            return dating_server_pb2.NeighboursReply(Keys=self.BDClient.search_near(request.Geo))
        except Exception as e:
            print("SetUser: got exception ::", e)
            return dating_server_pb2.NeighboursReply(ErrorMessage=str(e))
        return dating_server_pb2.SetUserReply(User=self.BDClient.read_user(request.User.Key))


def server():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dating_server_pb2_grpc.add_DatingServerServicer_to_server(DatingServer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    server()
