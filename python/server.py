from concurrent import futures
import logging

import sys, os
sys.path.append('./generated')

import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import user_utils
from base_client import CouchbaseClient

from misc import SetOkReplyStatus, SetErrorReply

class DatingServer(dating_server_pb2_grpc.DatingServerServicer):

    def __init__(self):
        super().__init__()
        self.BDClient = CouchbaseClient()

    def SimpleRequestProcessing(requestName:str, reply_class, make_kwargs):
        print(requestName)
        try :
            return SetOkReplyStatus(
                reply_class(make_kwargs())
            )
        except Exception as e:
            print(f"{requestName}: got exception ::", e)
            return SetErrorReply(reply_class(), str(e))


    def GetUser(self, request, context):
        return SimpleRequest(
            "GetUser",
            dating_server_pb2.GetUserReply,
            lambda : {
                "User"=self.BDClient.read_user(request.Key)
            }
        )

        # print("GetUser")
        # try :
        #     return SetOkReplyStatus(
        #         dating_server_pb2.GetUserReply(
        #             User=self.BDClient.read_user(request.Key)
        #         )
        #     )
        # except Exception as e:
        #     print("GetUser: got exception ::", e)
        #     return SetErrorReply(dating_server_pb2.GetUserReply(), str(e))

    def SetUser(self, request, context):
        def make_kwargs():
            self.BDClient.insert_user(request.User)
            return {}

        return SimpleRequest(
            "SetUser",
            dating_server_pb2.SetUserReply,
            make_kwargs
        )
        # print("SetUser")
        # try :
        #     self.BDClient.insert_user(request.User)
        #     return SetOkReplyStatus(dating_server_pb2.SetUserReply())
        # except Exception as e:
        #     print("SetUser: got exception ::", e)
        #     return SetErrorReply(dating_server_pb2.SetUserReply(), str(e))

    def SearchAllNeighbours(self, request, context):
        return SimpleRequest(
            "SearchAllNeighbours",
            dating_server_pb2.NeighboursReply,
            lambda : {
                "Keys"=self.BDClient.search_near(request.Geo, request.Distance)
            }
        )
        # print("SearchAllNeighbours")
        # try :
        #     return SetOkReplyStatus(
        #         dating_server_pb2.NeighboursReply(
        #             Keys=self.BDClient.search_near(request.Geo, request.Distance)
        #         )
        #     )
        # except Exception as e:
        #     print("SearchAllNeighbours: got exception ::", e)
        #     return SetErrorReply(dating_server_pb2.NeighboursReply(), str(e))

    def FindNearest(self, request, context):
        return SimpleRequest(
            "FindNearest",
            dating_server_pb2.NearestReply,
            lambda : {
                "User"=self.BDClient.get_nearest(request.Geo)
            }
        )
        # print("FindNearest")
        # try :
        #     return SetOkReplyStatus(
        #         dating_server_pb2.NearestReply(
        #             User=self.BDClient.get_nearest(request.Geo)
        #         )
        #     )
        # except Exception as e:
        #     print("FindNearest: got exception ::", e)
        #     return SetErrorReply(dating_server_pb2.NearestReply(), str(e))

    def GetReactions(self, request, context):
        def make_kwargs():
            if request.WhichOneof("Key") is None:
                raise Exception("Empty request")
            if request.HasField("From"):
                return {
                    "Reactions"=self.BDClient.get_reactions_from(request.From)
                }
            if request.HasField("To"):
                return {
                    "Reactions"=self.BDClient.get_reactions_to(request.To)
                }

        return SimpleRequest(
            "GetReactions",
            dating_server_pb2.GetReactionsReply,
            make_kwargs
        )

    def SetReaction(self, request, context):
        def make_kwargs():
            self.BDClient.set_reaction(request.From, request.To, request.Reaction)
            return {}

        return SimpleRequest(
            "SetReaction",
            dating_server_pb2.SetReactionReply,
            make_kwargs
        )


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
