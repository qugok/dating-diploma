from datetime import timedelta
import generated.user_pb2 as user_pb2
from lib.config import read_config_from

import generated.config_pb2 as config_pb2

# needed for any cluster connection
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               QueryOptions, UpsertOptions, GetOptions, SearchOptions, InsertOptions, ReplaceOptions)
from couchbase.transcoder import RawBinaryTranscoder
import couchbase.search as search
from couchbase.logic.search_queries import GeoDistanceQuery, TermQuery
from couchbase.logic.search import SortGeoDistance

from google.protobuf.json_format import MessageToDict

from lib.misc import DictToMessage

import uuid
import time

import logging

logger = logging.getLogger(__name__)

class CouchbaseClient:
    def __init__(self, config_path, server = 'couchbase://127.0.0.1'):
        configs = read_config_from(config_pb2.TPrivateData, config_path)
        auth = PasswordAuthenticator(
            configs.Username,
            configs.Password,
        )
        self.cluster = Cluster(server, ClusterOptions(auth))
        self.cluster.wait_until_ready(timedelta(seconds=5))
        self.bucket = self.cluster.bucket("dating-data")
        self.user_data_collection = self.bucket.scope("protobufs").collection("user_data")
        self.user_data_transcoder = RawBinaryTranscoder()

        self.geo_data_collection = self.bucket.scope("indexing_jsons").collection("geo_data")
        self.reactions_collection = self.bucket.scope("indexing_jsons").collection("reactions_data")
        self.messages_collection = self.bucket.scope("indexing_jsons").collection("messages_data")

    def __get_user(self, UID: str):
        result = self.user_data_collection.get(UID, GetOptions(transcoder=self.user_data_transcoder))
        user = user_pb2.TUser()
        user.ParseFromString(result.content_as[bytes])
        return user, result.cas

    def get_user(self, UID: str):
        return self.__get_user(UID)[0]


    def insert_user(self, user: user_pb2.TUser):
        result = self.user_data_collection.insert(
            user.UID,
            user.SerializeToString(),
            InsertOptions(transcoder=self.user_data_transcoder)
        )
        print(result)

    def update_user(self, user_delta: user_pb2.TUser):
        """
        если пользователь успевает измениться за время выполнения, то кидает исключение CASMismatchException
        """

        user, old_cas = self.__get_user(user.UID)
        user.MergeFrom(user_delta)

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
            "geo_user",
            GeoDistanceQuery(distance, (geo.Longitude, geo.Latitude)),
            SearchOptions(
                limit=limit,
                sort = [SortGeoDistance((geo.Longitude, geo.Latitude), "geo")]
            )
        )
        UIDs = [row.id for row in result.rows()]
        return UIDs

    def get_reactions_with(self, UID: str):
        #  TODO научиться в SDK искать в конкретном поле а не во всех
        #  TODO переименовать в reactions_index или что-то подобное, чтобы сразу было понятно что поиск идёт по индексу
        print(list(user_pb2.TReaction.DESCRIPTOR.fields_by_name), flush=True)
        result = self.cluster.search_query(
            "reactions",
            TermQuery(UID),
            SearchOptions(fields=list(user_pb2.TReaction.DESCRIPTOR.fields_by_name))
        )

        reactions = [
            DictToMessage(row.fields, user_pb2.TReaction)
            for row in result
        ]
        return reactions


    def upsert_reaction(
        self,
        reaction: user_pb2.TReaction
    ):
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
        message.Timestamp = time.time_ns()
        self.messages_collection.upsert(
            str(uuid.uuid4()),
            MessageToDict(message)
        )


    def read_messages_with(
        self,
        UID: str,
    ):
        result = self.cluster.search_query(
            "messages_index",
            TermQuery(UID),
            SearchOptions(fields=list(user_pb2.TMessage.DESCRIPTOR.fields_by_name))
        )

        messages = [
            DictToMessage(row.fields, user_pb2.TMessage)
            for row in result
        ]

        return messages
