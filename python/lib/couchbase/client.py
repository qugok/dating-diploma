import logging

from datetime import timedelta
import generated.user_pb2 as user_pb2
from lib.config import read_config_from
from lib.exceptions import UserDontExist, KeyDontExist, KeyAlreadyExist

import generated.config_pb2 as config_pb2

# needed for any cluster connection
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               QueryOptions, UpsertOptions, GetOptions, SearchOptions, InsertOptions, ReplaceOptions, ExistsOptions)
from couchbase.transcoder import RawBinaryTranscoder
import couchbase.search as search
from couchbase.logic.search_queries import GeoDistanceQuery
from couchbase.logic.search import SortGeoDistance

from google.protobuf.json_format import MessageToDict

from lib.misc import DictToMessage, get_timestamp

import uuid

logger = logging.getLogger("lib")

class CouchbaseClient:
    def __init__(self, config_path):
        configs = read_config_from(config_pb2.TPrivateData, config_path)
        auth = PasswordAuthenticator(
            configs.CouchbaseUsername,
            configs.CouchbasePassword,
        )

        self.cluster = Cluster(configs.CouchbaseAddress, ClusterOptions(auth))
        self.cluster.wait_until_ready(timedelta(seconds=30))
        self.bucket = self.cluster.bucket("dating-data")
        self.user_data_collection = self.bucket.scope("protobufs").collection("user_data")
        self.user_data_transcoder = RawBinaryTranscoder()

        self.geo_data_collection = self.bucket.scope("indexing_jsons").collection("geo_data")
        self.reactions_collection = self.bucket.scope("indexing_jsons").collection("reactions_data")
        self.messages_collection = self.bucket.scope("indexing_jsons").collection("messages_data")
        self.chats_collection = self.bucket.scope("indexing_jsons").collection("chats_data")
        self.message_token_collection = self.bucket.scope("key_value").collection("message_token")

    def get_message_token(self, UID:str):
        if not self.has_message_token(UID):
            raise KeyDontExist("message_token", UID)
        result = self.message_token_collection.get(UID)
        return result.content_as[str]

    def has_message_token(self, UID:str):
        result = self.message_token_collection.exists(UID)
        return result.exists

    def set_message_token(self, UID:str, token:str):
        self.message_token_collection.upsert(
            UID,
            token
        )

    def __get_user(self, UID: str):
        logger.debug(f"getting user {UID} from state")
        if not self.has_user(UID):
            raise UserDontExist()
        result = self.user_data_collection.get(UID, GetOptions(transcoder=self.user_data_transcoder))
        user = user_pb2.TUser()
        user.ParseFromString(result.content_as[bytes])
        return user, result.cas

    def has_user(self, UID: str):
        result = self.user_data_collection.exists(UID)
        return result.exists

    def get_user(self, UID: str):
        return self.__get_user(UID)[0]


    def insert_user(self, user: user_pb2.TUser):
        self.user_data_collection.insert(
            user.UID,
            user.SerializeToString(),
            InsertOptions(transcoder=self.user_data_transcoder)
        )

    def update_user(self, user_delta: user_pb2.TUser):
        """
        если пользователь успевает измениться за время выполнения, то кидает исключение CASMismatchException
        """

        user, old_cas = self.__get_user(user_delta.UID)
        user.MergeFrom(user_delta)
        if len(user_delta.Media) > 0:
            del user.Media[:]
            user.Media.extend(user_delta.Media)
        if user_delta.HasField("Interests"):
            user.Interests.CopyFrom(user_delta.Interests)

        self.user_data_collection.replace(
            user.UID,
            user.SerializeToString(),
            ReplaceOptions(transcoder=self.user_data_transcoder, cas=old_cas)
        )

    def upsert_to_geo_index(self, UID: str, geo: user_pb2.TGeo):
        self.geo_data_collection.upsert(
            UID,
            {
                "geo": {
                    "lat" : geo.Latitude,
                    "lon" : geo.Longitude
                }
            }
        )

    def search_near(self, geo: user_pb2.TGeo, distance, limit):
        result = self.cluster.search_query(
            "geo_index",
            GeoDistanceQuery(distance, (geo.Longitude, geo.Latitude)),
            SearchOptions(
                limit=limit,
                sort = [SortGeoDistance((geo.Longitude, geo.Latitude), "geo")]
            )
        )
        UIDs = [row.id for row in result.rows()]
        return UIDs

    def get_reactions_from(self,
        FromUID: str,
        only_matches:bool,
        offset=0,
        limit=100,
    ):

        only_matches_str = "AND IsMatch=true" if only_matches else ""

        query = f"""
        SELECT *
        FROM `dating-data`.indexing_jsons.reactions_data
        WHERE FromUID=$uid {only_matches_str}
        ORDER BY Timestamp DESC
        OFFSET $offset
        LIMIT $limit"""
        result = self.cluster.query(query, uid=FromUID, offset=offset, limit=limit)

        reactions = [
            DictToMessage(row['reactions_data'], user_pb2.TReaction)
            for row in result
        ]
        return reactions

    def get_reactions_to(self,
        ToUID: str,
        only_matches:bool,
        offset=0,
        limit=100,
    ):

        only_matches_str = "AND IsMatch=true" if only_matches else ""
        query = f"""
        SELECT *
        FROM `dating-data`.indexing_jsons.reactions_data
        WHERE ToUID=$uid {only_matches_str}
        ORDER BY Timestamp DESC
        OFFSET $offset
        LIMIT $limit"""
        result = self.cluster.query(query, uid=ToUID, offset=offset, limit=limit)
        reactions = [
            DictToMessage(row['reactions_data'], user_pb2.TReaction)
            for row in result
        ]
        return reactions

    def has_reaction(self, FromUID:str, ToUID:str):
        key = FromUID + "_" + ToUID
        result = self.reactions_collection.exists(key)
        return result.exists

    def get_reaction(self, FromUID:str, ToUID:str):
        key = FromUID + "_" + ToUID
        if not self.has_reaction(FromUID, ToUID):
            return None
        result = self.reactions_collection.get(
            key,
        )
        reaction = DictToMessage(result.content_as[dict], user_pb2.TReaction)
        return reaction

    def get_reactions(self, FromUID:str, ToUIDs:list):
        query = f"""
        SELECT *
        FROM `dating-data`.indexing_jsons.reactions_data
        WHERE (FromUID=$fromUID and ToUID in $uids) or (ToUID=$fromUID and FromUID in $uids)
        """
        result = self.cluster.query(query, fromUID=FromUID, uids=ToUIDs)
        reactions = [
            DictToMessage(row['reactions_data'], user_pb2.TReaction)
            for row in result
        ]
        from_reqctions = {r.ToUID:r for r in reactions if r.FromUID == FromUID}
        to_reqctions = {r.FromUID:r for r in reactions if r.ToUID == FromUID}
        return {uid:(from_reqctions.get(uid), to_reqctions.get(uid)) for uid in ToUIDs}

    def upsert_reaction(
        self,
        reaction: user_pb2.TReaction
    ):

        reaction.Timestamp = get_timestamp()
        self.reactions_collection.upsert(
            reaction.FromUID + "_" + reaction.ToUID,
            MessageToDict(reaction)
        )

    def store_messages(
        self,
        messages # repeated user_pb2.TMessage,
    ):
        for message in messages:
            self.__store_message(message)

    def __store_message(
        self,
        message: user_pb2.TMessage,
    ):
        message.Timestamp = get_timestamp()
        self.messages_collection.upsert(
            str(uuid.uuid4()),
            MessageToDict(message)
        )

    def read_messages(
        self,
        UID1: str,
        UID2: str,
        offset=0,
        limit=100,
    ):
        query = """
        SELECT *
        FROM `dating-data`.indexing_jsons.messages_data
        WHERE (FromUID=$uid1 AND ToUID=$uid2) OR (FromUID=$uid2 AND ToUID=$uid1)
        ORDER BY Timestamp DESC
        OFFSET $offset
        LIMIT $limit"""
        result = self.cluster.query(query, uid1=UID1, uid2=UID2, offset=offset, limit=limit)

        messages = [
            DictToMessage(row['messages_data'], user_pb2.TMessage)
            for row in result
        ]

        return messages

    def get_chat(self, key:str):
        result = self.chats_collection.get(
            key,
        )
        chat = DictToMessage(result.content_as[dict], user_pb2.TChat)
        return chat

    def get_chats(
        self,
        UID: str,
        offset=0,
        limit=100,
    ):

        query = """
        SELECT *
        FROM `dating-data`.indexing_jsons.chats_data
        WHERE UID1=$uid OR UID2=$uid
        ORDER BY LastMessage.Timestamp DESC
        OFFSET $offset
        LIMIT $limit"""
        result = self.cluster.query(query, uid=UID, offset=offset, limit=limit)

        chats = [
            DictToMessage(row['chats_data'], user_pb2.TChat)
            for row in result
        ]
        return chats

    def upsert_chat(
        self,
        chat: user_pb2.TChat,
    ):
        self.chats_collection.upsert(
            chat.UID1 + "_" + chat.UID2,
            MessageToDict(chat)
        )
