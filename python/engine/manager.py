import generated.user_pb2 as user_pb2
import generated.config_pb2 as config_pb2
from lib.couchbase.client import CouchbaseClient
from engine.pusher import Pusher
from lib.tools.proto_utils import FullMessageToDict
from lib.exceptions import UserDontExist, KeyDontExist, KeyAlreadyExist
from lib.misc import get_time_delta

from itertools import zip_longest, chain


import logging
import time
from datetime import datetime

from google.protobuf.json_format import MessageToDict

logger = logging.getLogger("engine")


class Manager:
    def __init__(self, config:config_pb2.TEngineConfig):
        self.couchbase_client = CouchbaseClient(config.PrivateDataPath)
        self.pusher = Pusher(config)

    def register_user(self, user: user_pb2.TUser):
        if self.couchbase_client.has_user(user.UID):
            raise KeyAlreadyExist("user_data", user.UID)
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

    def __get_and_order_sutable_users(self, user: user_pb2.TUser, uids):
        user_interests = {interest.Type : interest.Value for interest in user.Interests.Interests}
        def check_user(u: user_pb2.TUser):
            if u.UID == user.UID:
                return False
            users_lookung_for_gender = user.Interests.LookingForGender or user.LookingForGenderDeprecated or user_pb2.EG_FEMALE
            other_lookung_for_gender = u.Interests.LookingForGender or u.LookingForGenderDeprecated or user_pb2.EG_FEMALE
            # remove if all users should have looking for gender
            if u.Gender != users_lookung_for_gender or \
                user.Gender != other_lookung_for_gender:
                return False
            if not (u.Interests.AgeFrom <= user.Age <= u.Interests.AgeTo and
                    user.Interests.AgeFrom <= u.Age <= user.Interests.AgeTo):
                return False
            return True

        def suitability(interests_proto:user_pb2.TInterests):
            anti_suitability = 0
            interests = {interest.Type : interest.Value for interest in interests_proto.Interests}
            for interest, value in user_interests.items():
                if interest not in interests:
                    anti_suitability += 1
                    continue
                anti_suitability += pow(value - interests[interest], 2)
            return -anti_suitability
        users = [self.couchbase_client.get_user(uid) for uid in uids]
        filtered_users = [u for u in users if check_user(u)]
        sorted_users = sorted(filtered_users, key=lambda u: suitability(u.Interests))
        logger.debug(f"filtered and sorted users: {[(FullMessageToDict(u), suitability(u.Interests)) for u in sorted_users]}")
        return sorted_users

    def get_users_to_show(self, UID:str, geo=None, distance:int=None, limit:int=None):
        def is_liked(reactionFrom:user_pb2.TReaction, reactionTo:user_pb2.TReaction):
            if reactionFrom is not None and get_time_delta(reactionFrom.Timestamp).days < 30:
                return False
            if reactionTo is not None and reactionTo.ReactionType == user_pb2.TReaction.ERT_LIKE:
                return True
            return False

        def has_not_dislike(reactionFrom:user_pb2.TReaction, reactionTo:user_pb2.TReaction):
            if reactionTo is not None:
                return False
            if reactionFrom is not None and reactionFrom.ReactionType == user_pb2.TReaction.ERT_DISLIKE:
                return False
            return True

        user = self.couchbase_client.get_user(UID)


        distance = distance or user.SearchDistanceKm or 100000
        limit = limit or 100
        geo = geo or user.LastGeo
        logger.info(f"get_users_to_show for UID: {UID} distance: {distance} limit: {limit} geo: {MessageToDict(geo)}")
        uids = [uid for uid in self.couchbase_client.search_near(geo, f"{distance}km", limit) if uid != UID]
        reactions = self.couchbase_client.get_reactions(UID, uids)
        must_have = self.__get_and_order_sutable_users(
            user,
            [uid for uid, rs in reactions.items() if is_liked(*rs)]
        )
        others = self.__get_and_order_sutable_users(
            user,
            [uid for uid, rs in reactions.items() if has_not_dislike(*rs)]
        )
        users_queue = chain.from_iterable(zip_longest(others, must_have, fillvalue=None))
        users = [user for user in users_queue if user is not None]
        return users

    def get_reactions(self, FromUID:str, ToUID:str, only_matches:bool, offset=0, limit=100):
        logger.debug(f"manager::get_reactions FromUID: {FromUID} ToUID: {ToUID}")
        if not ToUID:
            return self.couchbase_client.get_reactions_from(FromUID, only_matches, offset, limit)
        if not FromUID:
            return self.couchbase_client.get_reactions_to(ToUID, only_matches, offset, limit)
        if self.couchbase_client.has_reaction(FromUID, ToUID):
            return [self.couchbase_client.get_reaction(FromUID, ToUID)]
        return []

    def insert_reaction(
        self,
        FromUID: str,
        ToUID: str,
        ReactionType: user_pb2.TReaction.EReactionType
    ):
        """
        добавляет реакцию, ~~только если её не было раньше, иначе выбрасывает исключение~~ всегда добавляет реакцию и приводит в

        """
        reaction = user_pb2.TReaction(FromUID=FromUID, ToUID=ToUID, ReactionType=ReactionType)
        other_reaction = self.couchbase_client.get_reaction(ToUID, FromUID)

        if other_reaction is not None and ReactionType == user_pb2.TReaction.ERT_LIKE == other_reaction.ReactionType:
            is_match = True
            if other_reaction.IsMatch == False:
                other_reaction.IsMatch = True
                self.couchbase_client.upsert_reaction(other_reaction)
        elif other_reaction is not None:
            is_match = False
            if other_reaction.IsMatch == True:
                other_reaction.IsMatch = False
                self.couchbase_client.upsert_reaction(other_reaction)
        else:
            is_match = False

        reaction.IsMatch = is_match
        self.couchbase_client.upsert_reaction(reaction)

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
        offset=0,
        limit=100
    ):
        messages = self.couchbase_client.read_messages(FromUID, ToUID, offset, limit)
        return messages

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
        offset=0,
        limit=100
    ):
        return self.couchbase_client.get_chats(UID, offset, limit)
