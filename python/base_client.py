from datetime import timedelta
import generated.user_pb2 as user_pb2
from config import read_configs

# needed for any cluster connection
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               QueryOptions, UpsertOptions, GetOptions, SearchOptions)
from couchbase.transcoder import RawBinaryTranscoder
import couchbase.search as search
from couchbase.logic.search_queries import GeoDistanceQuery, TermQuery
from couchbase.logic.search import SortGeoDistance


from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import ParseDict
from google.protobuf.json_format import MessageToDict

import uuid
import time

# Update this to your cluster
# private_data = read_configs()
# username = private_data.Username
# password = private_data.Password
# bucket_name = "travel-sample"
# bucket_name = "object-data"
# User Input ends here.

# Connect options - authentication
# auth = PasswordAuthenticator(
#     username,
#     password,
# )

def run_with_try_except(func):
    #  TODO REFACTORING заменить на нормальный декоратор
    try:
        return func()
    except Exception as e:
        print(e)
        raise e

class CouchbaseClient:
    def __init__(self, server = 'couchbase://127.0.0.1', configs = read_configs()):
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

    def insert_user(self, user: user_pb2.TUser):
        def proc():
            self.__insert_user(user)
            self.__insert_to_external(user)

        return run_with_try_except(proc)


    def __insert_user(self, user: user_pb2.TUser):
        #  TODO: разобраться когда нужно использовать upsert, insert, replace а не использовать бездумно как сейчас
        result = self.user_data_collection.upsert(
            user.UID,
            user.SerializeToString(),
            UpsertOptions(transcoder=self.user_data_transcoder)
        )
        print(result)

    def read_user(self, UID: str):

        return run_with_try_except(lambda : self.__read_user(UID))

    def __read_user(self, UID: str):
        result = self.user_data_collection.get(UID, GetOptions(transcoder=self.user_data_transcoder))
        user = user_pb2.TUser()
        user.ParseFromString(result.content_as[bytes])
        return user

    def __insert_to_external(self, user: user_pb2.TUser):
        if not user.HasField("LastGeo"):
            return
        def proc():
            result = self.geo_data_collection.upsert(
                user.UID,
                {
                    "geo": {
                        "lat" : user.LastGeo.Latitude,
                        "lon" : user.LastGeo.Longitude
                    }
                }
            )
            print(result)

        return run_with_try_except(proc)

    def search_near(self, geo: user_pb2.TGeo, distance = None):
        distance = distance or "100km"
        print("dist:", distance)

        def proc():
            result = self.cluster.search_query(
                "geo_user",
                GeoDistanceQuery(distance, (geo.Longitude, geo.Latitude)),
                SearchOptions(limit=10)
            )
            UIDs = [row.id for row in result.rows()]
            return UIDs

        return run_with_try_except(proc)

    def get_nearest(self, geo: user_pb2.TGeo):
        def proc():
            result = self.cluster.search_query(
                "geo_user",
                GeoDistanceQuery("30000km", (geo.Longitude, geo.Latitude)),
                SearchOptions(
                    sort = [SortGeoDistance((geo.Longitude, geo.Latitude), "geo")]
                )
            )
            UID = list(result)[0].id
            return self.__read_user(UID)

        return run_with_try_except(proc)

    def get_reactions_with(self, UID: str):
        def proc():
            #  TODO научиться в SDK искать в конкретном поле а не во всех
            #  TODO переименовать в reactions_index или что-то подобное, чтобы сразу было понятно что поиск идёт по индексу
            result = self.cluster.search_query(
                "reactions",
                TermQuery(UID),
                SearchOptions(fields=["fr", "to", "reaction"])
            )

            reactions = [user_pb2.TReaction(
                    FromUID = row.fields["fr"],
                    ToUID = row.fields["to"],
                    ReactionType = row.fields["reaction"]
                )
                for row in result
            ]
            return reactions

        return run_with_try_except(proc)

    def set_reaction(
        self,
        fr: str,
        to: str,
        reaction: user_pb2.TReaction.EReactionType
    ):
        def proc():
            result = self.reactions_collection.upsert(
                fr + "_" + to,
                {
                    "fr" : fr,
                    "to" : to,
                    "reaction" : reaction,
                }
            )

        return run_with_try_except(proc)

    def store_messages(
        self,
        messages # repeated user_pb2.TMessage,
    ):
        def proc():
            for message in messages:
                self.__store_message(message)


        return run_with_try_except(proc)

    def __store_message(
        self,
        message: user_pb2.TMessage,
    ):
        # TODO убрать заполнение полей из класса для общения с бд в отдельный класс (мб Engine)
        message.Timestamp = time.time_ns()
        result = self.messages_collection.upsert(
            str(uuid.uuid4()),
            MessageToDict(message)
        )


    def read_messages(
        self,
        fr: str,
        to: str,
    ):
        def proc():
            def read_message(js_dict):
                print(js_dict)
                message = user_pb2.TMessage()
                message.ToUID = js_dict['ToUID']
                message.FromUID = js_dict['FromUID']
                message.Timestamp = int(js_dict['Timestamp'])
                message.Text = js_dict['Text']
                # ParseDict(js_dict, message)
                return message
            #  TODO научиться в SDK искать в конкретном поле а не во всех
            # message: user_pb2.TMessage
            result = self.cluster.search_query(
                "messages_index",
                TermQuery(fr),
                SearchOptions(fields=['FromUID', 'ToUID', 'Timestamp', 'Text'])
            )

            messages = [
                read_message(row.fields)
                for row in result
            ]

            messages = [
                message
                for message in messages
                if message.FromUID == fr and message.ToUID == to
            ]
            return messages

        return run_with_try_except(proc)

# Get a reference to our cluster
# NOTE: For TLS/SSL connection use 'couchbases://<your-ip-address>' instead
# cluster = Cluster('couchbase://localhost', ClusterOptions(auth))
# cluster = Cluster('couchbase://127.0.0.1', ClusterOptions(auth))

# Wait until the cluster is ready for use.
# cluster.wait_until_ready(timedelta(seconds=5))

# get a reference to our bucket
# cb = cluster.bucket("dating-data")

# user_data_collection = cb.scope("protobufs").collection("user_data")

# Get a reference to the default collection, required for older Couchbase server versions
# cb_coll_default = cb.default_collection()
# transcoder = RawBinaryTranscoder()

# upsert document function
