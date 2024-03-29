

# import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import generated.config_pb2 as config_pb2

from lib.tools.decorators import process_simple_request
from lib.auth import FirebaseApp
from lib.validate_request import Validator
from engine.manager import Manager

import logging

logger = logging.getLogger("engine")

class DatingServerEngine(dating_server_pb2_grpc.DatingServerServicer):
    # TODO научиться передавать ошибки не через поля, а в идеале и авторизацию

    def __init__(self, config):
        super().__init__()
        self.auth = FirebaseApp(config.Auth)
        self.validator = Validator()

        self.logger = logger
        self.manager = Manager(config)

    @process_simple_request(dating_server_pb2.GetUserReply)
    def GetUser(self, request, context, user_auth_info):
        return {"User": self.manager.get_user(request.UID)}

    @process_simple_request(dating_server_pb2.RegisterUserReply)
    def RegisterUser(self, request, context, user_auth_info):
        self.manager.register_user(request.User)
        return {}

    @process_simple_request(dating_server_pb2.UpdateUserReply)
    def UpdateUser(self, request, context, user_auth_info):
        self.manager.update_user(request.UserDelta)
        return {}

    @process_simple_request(dating_server_pb2.SearchUsersReply)
    def SearchUsers(self, request :dating_server_pb2.SearchUsersRequest, context, user_auth_info):
        return {"Users":self.manager.get_users_to_show(request.UID, request.Geo, distance=request.Distance)}

    @process_simple_request(dating_server_pb2.SetMessageTokenReply)
    def SetMessageToken(self, request:dating_server_pb2.SetMessageTokenRequest, context, user_auth_info):
        self.manager.install_message_token(request.UID, request.Token)
        return {}

    @process_simple_request(dating_server_pb2.GetReactionsReply)
    def GetReactions(self, request:dating_server_pb2.GetReactionsRequest, context, user_auth_info):
        limit = request.Count or 100
        offset = request.Offset or 0
        only_matches = request.OnlyMatches or False
        return {"Reactions":self.manager.get_reactions(request.FromUID, request.ToUID, only_matches, offset, limit)}

    @process_simple_request(dating_server_pb2.SetReactionReply)
    def SetReaction(self, request, context, user_auth_info):
        return {"Match": self.manager.insert_reaction(request.FromUID, request.ToUID, request.Reaction)}


    @process_simple_request(dating_server_pb2.SendMessageReply)
    def SendMessage(self, request, context, user_auth_info):
        self.manager.send_messages(request.Messages)
        return {}

    @process_simple_request(dating_server_pb2.GetLastMessagesReply)
    def GetLastMessages(self, request, context, user_auth_info):
        limit = request.Count or 100
        offset = request.Offset or 0
        return {"Messages" : self.manager.read_messages(request.FromUID, request.ToUID, offset, limit)}

    @process_simple_request(dating_server_pb2.GetChatsReply)
    def GetChats(self, request, context, user_auth_info):
        limit = request.Count or 100
        offset = request.Offset or 0
        return {"Chats" : self.manager.get_chats(request.UID, offset, limit)}
