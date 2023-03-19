from concurrent import futures
import logging

import sys

import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import user_utils
from base_client import CouchbaseClient

from misc import SetOkReplyStatus, SetErrorReply
from validation import validate_user, validate_set_reaction

import traceback


def process_simple_request(reply_class):
    def real_decorator(request_func=None):
        def wrapper(self, request, context):
            # TODO заменить print на нормальное логгирование
            print("processing", request_func.__name__)
            try :
                kws = request_func(self, request, context)
                return SetOkReplyStatus(
                    reply_class(**kws)
                )
            except Exception as e:
                print(f"{request_func.__name__}: got exception ::", e)
                return SetErrorReply(reply_class(), str(e) + str(traceback.format_exc()))
        return wrapper
    return real_decorator

class DatingServer(dating_server_pb2_grpc.DatingServerServicer):

    def __init__(self):
        super().__init__()
        self.BDClient = CouchbaseClient()

    @process_simple_request(dating_server_pb2.GetUserReply)
    def GetUser(self, request, context):
        return {"User": self.BDClient.read_user(request.UID)}

    @process_simple_request(dating_server_pb2.SetUserReply)
    def SetUser(self, request, context):
        print(request)
        validate_user(request.User)
        self.BDClient.insert_user(request.User)
        return {}

    @process_simple_request(dating_server_pb2.NeighboursReply)
    def SearchAllNeighbours(self, request, context):
        return {"UIDs":self.BDClient.search_near(request.Geo, request.Distance)}

    @process_simple_request(dating_server_pb2.NearestReply)
    def FindNearest(self, request, context):
        return {"User":self.BDClient.get_nearest(request.Geo)}

    @process_simple_request(dating_server_pb2.GetReactionsReply)
    def GetReactions(self, request, context):
        field_name = request.WhichOneof("Key")
        if field_name is None:
            raise Exception("Empty request")
        reactions = self.BDClient.get_reactions_with(getattr(request, field_name))
        if field_name == "FromUID":
            reactions = [react for react in reactions if react.FromUID == request.FromUID]
        if field_name == "ToUID":
            reactions = [react for react in reactions if react.ToUID == request.ToUID]

        return {"Reactions":reactions}

    @process_simple_request(dating_server_pb2.SetReactionReply)
    def SetReaction(self, request, context):
        validate_set_reaction(request)
        self.BDClient.set_reaction(request.FromUID, request.ToUID, request.Reaction)
        return {}


    @process_simple_request(dating_server_pb2.SendMessageReply)
    def SendMessage(self, request, context):
        self.BDClient.store_messages(request.Messages)
        return {}

    @process_simple_request(dating_server_pb2.GetLastMessagesReply)
    def GetLastMessages(self, request, context):
        return {"Messages" : self.BDClient.read_messages(request.FromUID, request.ToUID)}


def server():
    # TODO вынести порт в аргументны
    port = '50051'
    print("adfgaergaergaergv", flush=True)
    print("adfgaergaergaadfgaergv", file=sys.stderr, flush=True)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dating_server_pb2_grpc.add_DatingServerServicer_to_server(DatingServer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port, flush=True)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    server()
