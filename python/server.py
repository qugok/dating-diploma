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
from validation import validate_user, validate_set_reaction

class DatingServer(dating_server_pb2_grpc.DatingServerServicer):

    def __init__(self):
        super().__init__()
        self.BDClient = CouchbaseClient()

    def SimpleRequestProcessing(requestName:str, reply_class, make_kwargs):
        print(requestName)
        try :
            kws = make_kwargs()
            return SetOkReplyStatus(
                reply_class(**kws)
            )
        except Exception as e:
            print(f"{requestName}: got exception ::", e)
            return SetErrorReply(reply_class(), str(e))


    def GetUser(self, request, context):
        return DatingServer.SimpleRequestProcessing(
            "GetUser",
            dating_server_pb2.GetUserReply,
            lambda : {
                "User": self.BDClient.read_user(request.Key)
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
            validate_user(request.User)
            self.BDClient.insert_user(request.User)
            return {}

        return DatingServer.SimpleRequestProcessing(
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
        return DatingServer.SimpleRequestProcessing(
            "SearchAllNeighbours",
            dating_server_pb2.NeighboursReply,
            lambda : {
                "Keys":self.BDClient.search_near(request.Geo, request.Distance)
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
        return DatingServer.SimpleRequestProcessing(
            "FindNearest",
            dating_server_pb2.NearestReply,
            lambda : {
                "User":self.BDClient.get_nearest(request.Geo)
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
            field_name = request.WhichOneof("Key")
            if field_name is None:
                raise Exception("Empty request")
            reactions = self.BDClient.get_reactions_with(getattr(request, field_name))
            if field_name == "From":
                reactions = [react for react in reactions if react.From == request.From]
            if field_name == "To":
                reactions = [react for react in reactions if react.To == request.To]

            return {
                "Reactions":reactions
            }

        return DatingServer.SimpleRequestProcessing(
            "GetReactions",
            dating_server_pb2.GetReactionsReply,
            make_kwargs
        )

    def SetReaction(self, request, context):
        def make_kwargs():
            validate_set_reaction(request)
            self.BDClient.set_reaction(request.From, request.To, request.Reaction)
            return {}

        return DatingServer.SimpleRequestProcessing(
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
