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

# Update this to your cluster
private_data = read_configs()
username = private_data.Username
password = private_data.Password
# bucket_name = "travel-sample"
bucket_name = "object-data"
# User Input ends here.

# Connect options - authentication
auth = PasswordAuthenticator(
    username,
    password,
)

# Get a reference to our cluster
# NOTE: For TLS/SSL connection use 'couchbases://<your-ip-address>' instead
# cluster = Cluster('couchbase://localhost', ClusterOptions(auth))
cluster = Cluster('couchbase://127.0.0.1', ClusterOptions(auth))

# Wait until the cluster is ready for use.
cluster.wait_until_ready(timedelta(seconds=5))

# get a reference to our bucket
cb = cluster.bucket(bucket_name)

cb_coll = cb.scope("inventory").collection("airline")
user_data_collection = cb.scope("protobufs").collection("user_data")

# Get a reference to the default collection, required for older Couchbase server versions
cb_coll_default = cb.default_collection()
transcoder = RawBinaryTranscoder()

# upsert document function

def insert_user(user: user_pb2.TUser):
    try:
        result = user_data_collection.upsert(str(user.Key.Hash), user.SerializeToString(), UpsertOptions(transcoder=transcoder))
        print(result)
    except Exception as e:
        print(e)
        raise e

def read_user(key: user_pb2.TUserKey):
    try:
        result = user_data_collection.get(str(key.Hash), GetOptions(transcoder=transcoder))
        user = user_pb2.TUser()
        user.ParseFromString(result.content_as[bytes])
        return user
    except Exception as e:
        print(e)
        raise e


def insert_raw_data(key, data):
    print("\nInsert Data: ")
    try:
        result = cb_coll_default.upsert(key, data)
        print(result)
    except Exception as e:
        print(e)


def read_raw_data(key):
    print("\nRead Data: ")
    try:
        result = cb_coll_default.get(key)
        print(result.content_as[str])
        print(result)
        return result.content_as[str]
    except Exception as e:
        print(e)


# insert_raw_data("keyabra", "kadabra")

# print("returned: ", read_raw_data("keyabra"))

# upsert_document(airline)

# get_airline_by_key("airline_8091")

# lookup_by_callsign("CBS")
