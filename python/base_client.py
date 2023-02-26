from datetime import timedelta
import generated.user_pb2 as user_pb2
from config import read_configs
from misc import UserKeyToKeyString, UserKeyToKeyInteger

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

    def insert_user(self, user: user_pb2.TUser):
        def proc():
            self.__insert_user(user)
            self.__insert_to_external(user)

        return run_with_try_except(proc)


    def __insert_user(self, user: user_pb2.TUser):
        result = self.user_data_collection.upsert(
            UserKeyToKeyString(user.Key),
            user.SerializeToString(),
            UpsertOptions(transcoder=self.user_data_transcoder)
        )
        print(result)

    def read_user(self, key: user_pb2.TUserKey):

        return run_with_try_except(lambda : self.__read_user(key))

    def __read_user(self, key: user_pb2.TUserKey):
        result = self.user_data_collection.get(UserKeyToKeyString(key), GetOptions(transcoder=self.user_data_transcoder))
        user = user_pb2.TUser()
        user.ParseFromString(result.content_as[bytes])
        return user

    def __insert_to_external(self, user: user_pb2.TUser):
        if not user.HasField("LastGeo"):
            return
        def proc():
            result = self.geo_data_collection.upsert(
                UserKeyToKeyString(user.Key),
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
            keys = [user_pb2.TUserKey(Hash=int(row.id)) for row in result.rows()]
            return keys

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
            key = user_pb2.TUserKey(Hash=int(list(result)[0].id))
            return self.__read_user(key)

        return run_with_try_except(proc)

    def get_reactions_with(self, key: user_pb2.TUserKey):
        def proc():
            result = self.cluster.search_query(
                "reactions",
                TermQuery(UserKeyToKeyString(key)),
                SearchOptions(fields=["fr", "to", "reaction"])
            )

            reactions = [user_pb2.TReaction(
                    From=user_pb2.TUserKey(Hash=int(row.fields["fr"])),
                    To=user_pb2.TUserKey(Hash=int(row.fields["to"])),
                    ReactionType=row.fields["reaction"]
                )
                for row in result
            ]
            print("reacts:", reactions)
            return reactions

        return run_with_try_except(proc)

    def set_reaction(
        self,
        fr: user_pb2.TUserKey,
        to: user_pb2.TUserKey,
        reaction: user_pb2.TReaction.EReactionType
    ):
        def proc():
            result = self.reactions_collection.upsert(
                UserKeyToKeyString(fr) + "_" + UserKeyToKeyString(to),
                {
                    "fr" : UserKeyToKeyString(fr),
                    "to" : UserKeyToKeyString(to),
                    "reaction" : reaction,
                }
            )
            print(result)

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

# def insert_raw_data(key, data):
#     print("\nInsert Data: ")
#     try:
#         result = cb_coll_default.upsert(key, data)
#         print(result)
#     except Exception as e:
#         print(e)


# def read_raw_data(key):
#     print("\nRead Data: ")
#     try:
#         result = cb_coll_default.get(key)
#         print(result.content_as[str])
#         print(result)
#         return result.content_as[str]
#     except Exception as e:
#         print(e)


# insert_raw_data("keyabra", "kadabra")

# print("returned: ", read_raw_data("keyabra"))

# upsert_document(airline)

# get_airline_by_key("airline_8091")

# lookup_by_callsign("CBS")
