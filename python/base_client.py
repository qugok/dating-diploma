from datetime import timedelta
import generated.user_pb2 as user_pb2
from config import read_configs




# needed for any cluster connection
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               QueryOptions, UpsertOptions, GetOptions)
from couchbase.transcoder import RawBinaryTranscoder
import couchbase.search as search
from couchbase.logic.search_queries import GeoDistanceQuery

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

    def insert_user(self, user: user_pb2.TUser):
        try:
            self.__insert_user(user)
            self.__insert_to_external(user)
        except Exception as e:
            print(e)
            raise e

    def __insert_user(self, user: user_pb2.TUser):
        result = self.user_data_collection.upsert(
            str(user.Key.Hash),
            user.SerializeToString(),
            UpsertOptions(transcoder=self.user_data_transcoder)
        )
        print(result)

    def read_user(self, key: user_pb2.TUserKey):
        try:
            return self.__read_user(key)
        except Exception as e:
            print(e)
            raise e

    def __read_user(self, key: user_pb2.TUserKey):
        result = self.user_data_collection.get(str(key.Hash), GetOptions(transcoder=self.user_data_transcoder))
        user = user_pb2.TUser()
        user.ParseFromString(result.content_as[bytes])
        return user

    def __insert_to_external(self, user: user_pb2.TUser):
        if not user.HasField("LastGeo"):
            return
        def make_geo_format(user: user_pb2.TUser):
            return {
                "geo": {
                    "lat" : user.LastGeo.Latitude,
                    "lon" : user.LastGeo.Longitude
                }
            }
        try:
            result = self.geo_data_collection.upsert(
                str(user.Key.Hash),
                make_geo_format(user)
            )
            print(result)
        except Exception as e:
            print(e)
            raise e

    def search_near(self, geo: user_pb2.TGeo, distance = "100km"):
        try:
            result = self.cluster.search_query(
                "geo_user",
                GeoDistanceQuery(distance, (geo.Longitude, geo.Latitude))
            )
            keys = [user_pb2.TUserKey(Hash=int(row.id)) for row in result.rows()]
            print(keys)
            return keys
        except Exception as e:
            print(e)
            raise e

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

# def insert_user(user: user_pb2.TUser):
#     try:
#         result = user_data_collection.upsert(str(user.Key.Hash), user.SerializeToString(), UpsertOptions(transcoder=transcoder))
#         print(result)
#     except Exception as e:
#         print(e)
#         raise e

# def read_user(key: user_pb2.TUserKey):
#     try:
#         result = user_data_collection.get(str(key.Hash), GetOptions(transcoder=transcoder))
#         user = user_pb2.TUser()
#         user.ParseFromString(result.content_as[bytes])
#         return user
#     except Exception as e:
#         print(e)
#         raise e


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
