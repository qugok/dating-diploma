import generated.user_pb2 as user_pb2
from lib.couchbase.client import CouchbaseClient
from engine.pusher import Pusher
from lib.tools.proto_utils import FullMessageToDict

import logging
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger("engine")


class Manager:
    def __init__(self, config):
        self.couchbase_client = CouchbaseClient(config.PrivateDataPath)
        self.pusher = Pusher(config)

    def register_user(self, user: user_pb2.TUser):
        self.couchbase_client.insert_user(user)

        if user.HasField("LastGeo"):
            self.couchbase_client.upsert_to_geo_index(user.UID, user.LastGeo)

    def update_user(self, user_delta: user_pb2.TUser):
        self.couchbase_client.update_user(user_delta)

        if user_delta.HasField("LastGeo"):
            self.couchbase_client.upsert_to_geo_index(user_delta.UID, user_delta.LastGeo)

    def get_user(self, UID: str):
        return self.couchbase_client.get_user(UID)

    def install_message_token(self, UID:str, token:str):
        self.couchbase_client.set_message_token(UID, token)

    def get_users_to_show(self, UID:str, geo: None, distance:int=None, limit:int=None):
        # TODO добавить логики поиска подходящего человека
        user = self.couchbase_client.get_user(UID)
        distance = distance or user.SearchDistanceKm or 10
        limit = limit or 10
        geo = geo or user.LastGeo
        logger.info(f"get_users_to_show for UID: {UID} distance: {distance} limit: {limit} geo: {MessageToDict(geo)}")
        uids = self.couchbase_client.search_near(geo, f"{distance}km", limit)
        users = [self.couchbase_client.get_user(uid) for uid in uids]

        return users

    def get_reactions(self, FromUID:str, ToUID:str):
        logger.debug(f"manager::get_reactions FromUID: {FromUID} ToUID: {ToUID}")
        if not ToUID:
            return self.get_reactions_from(FromUID)
        if not FromUID:
            return self.get_reactions_to(ToUID)
        if self.couchbase_client.has_reaction(ToUID, FromUID):
            return [self.couchbase_client.get_reaction(ToUID, FromUID)]
        return []

    def get_reactions_from(self, UID:str):
        reactions = self.couchbase_client.get_reactions_with(UID)
        return [react for react in reactions if react.FromUID == UID]

    def get_reactions_to(self, UID:str):
        reactions = self.couchbase_client.get_reactions_with(UID)
        return [react for react in reactions if react.ToUID == UID]

    def insert_reaction(
        self,
        FromUID: str,
        ToUID: str,
        ReactionType: user_pb2.TReaction.EReactionType
    ):
        """
        добавляет реакцию, ~~только если её не было раньше, иначе выбрасывает исключение~~ всегда добавляет реакцию и приводит в
        TODO поставить ттл на реакции - пара месяцев
        """
        reaction = user_pb2.TReaction(FromUID=FromUID, ToUID=ToUID, ReactionType=ReactionType)
        other_reaction = self.couchbase_client.get_reaction(ToUID, FromUID)

        if other_reaction is None or ReactionType != user_pb2.TReaction.ERT_LIKE:
            is_match = False
        else:
            is_match = other_reaction.ReactionType == user_pb2.TReaction.ERT_LIKE
            other_reaction.IsMatch = is_match

        reaction.IsMatch = is_match
        self.couchbase_client.upsert_reaction(reaction)

        if other_reaction.IsMatch != is_match:
            other_reaction.IsMatch == is_match
            self.couchbase_client.upsert_reaction(other_reaction)

        self.pusher.send_reactions([reaction])

        return is_match

    def send_messages(
        self,
        messages # repeated user_pb2.TMessage,
    ):
        self.couchbase_client.store_messages(messages)
        self.pusher.send_messages(messages)
        self.set_chat_last_message(messages[-1])

    def read_messages(
        self,
        FromUID: str,
        ToUID: str,
    ):
        messages = self.couchbase_client.read_messages_with(FromUID)
        return [message for message in messages if message.FromUID == FromUID and message.ToUID == ToUID]

    def set_chat_last_message(
        self,
        message:user_pb2.TMessage
    ):
        UID1, UID2 = min(message.FromUID, message.ToUID), max(message.ToUID, message.FromUID)
        chat = user_pb2.TChat(UID1=UID1, UID2=UID2, LastMessage=message)
        self.couchbase_client.upsert_chat(chat)

    def get_chats(
        self,
        UID:str,
    ):
        return self.couchbase_client.get_chats(UID)
