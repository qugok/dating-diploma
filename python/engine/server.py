

# import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import generated.config_pb2 as config_pb2

from lib.tools.decorators import process_simple_request
from lib.auth import FirebaseAuth
from engine.manager import Manager

import logging

logger = logging.getLogger(__name__)

class DatingServerEngine(dating_server_pb2_grpc.DatingServerServicer):
    # TODO научиться передавать ошибки не через поля, а в идеале и авторизацию

    def __init__(self, config:config_pb2.TServerConfig):
        super().__init__()
        self.auth = FirebaseAuth(config.Auth)

        self.logger = logger
        self.manager = Manager(config.PrivateDataPath)

    @process_simple_request(dating_server_pb2.GetUserReply)
    def GetUser(self, request, context, user_auth_info):
        logger.info(f"Processiong GetUser with UID: {request.UID}")
        return {"User": self.manager.get_user(request.UID)}

    @process_simple_request(dating_server_pb2.RegisterUserReply)
    def RegisterUser(self, request, context, user_auth_info):
        logger.info(f"Processiong RegisterUser with UID: {request.User.UID}")
        self.manager.register_user(request.User)
        return {}

    @process_simple_request(dating_server_pb2.UpdateUserReply)
    def UpdateUser(self, request, context, user_auth_info):
        logger.info(f"Processiong UpdateUser with UID: {request.UserDelta.UID}")
        self.manager.update_user(request.UserDelta)
        return {}

    @process_simple_request(dating_server_pb2.SearchUsersReply)
    def SearchUsers(self, request :dating_server_pb2.SearchUsersRequest, context, user_auth_info):
        logger.info(f"Processiong SearchUsers with UID: {request.UID} Geo: {request.Geo.Latitude}, {request.Geo.Longitude} Dist: {request.Distance}")
        return {"Users":self.manager.get_users_to_show(request.UID, request.Geo, distance=request.Distance)}

    @process_simple_request(dating_server_pb2.GetReactionsReply)
    def GetReactions(self, request, context, user_auth_info):
        field_name = request.WhichOneof("Key")
        if field_name is None:
            raise Exception("Empty request")
        logger.info(f"Processiong GetReactions with {field_name}: {getattr(request, field_name)}")

        if field_name == "FromUID":
            reactions = self.manager.get_reactions_from(request.FromUID)
        if field_name == "ToUID":
            reactions = self.manager.get_reactions_to(request.ToUID)

        return {"Reactions":reactions}

    @process_simple_request(dating_server_pb2.SetReactionReply)
    def SetReaction(self, request, context, user_auth_info):
        logger.info(f"Processiong SetUser with FromUID: {request.FromUID} ToUID: {request.ToUID} Reaction: {request.Reaction}")
        self.manager.insert_reaction(request.FromUID, request.ToUID, request.Reaction)
        return {}


    @process_simple_request(dating_server_pb2.SendMessageReply)
    def SendMessage(self, request, context, user_auth_info):
        logger.info(f"Processiong SendMessage")
        self.manager.send_messages(request.Messages)
        return {}

    @process_simple_request(dating_server_pb2.GetLastMessagesReply)
    def GetLastMessages(self, request, context, user_auth_info):
        logger.info(f"Processiong GetLastMessages with FromUID: {request.FromUID} ToUID: {request.ToUID}")
        return {"Messages" : self.manager.read_messages(request.FromUID, request.ToUID)}
