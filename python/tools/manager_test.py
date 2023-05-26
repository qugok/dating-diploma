from lib.couchbase.client import CouchbaseClient
from engine.manager import Manager



import generated.user_pb2 as user_pb2
import generated.config_pb2 as config_pb2

config = config_pb2.TEngineConfig(
PrivateDataPath= "conf/private_data.pb.txt"
)


manager = Manager(config)

geo = user_pb2.TGeo(Latitude=55.706255, Longitude=37.521230)


# print(manager.get_users_to_show("bbbbbbbbbbbbbbbbbbbbbbbbb", geo=geo, distance=2))
print(manager.read_messages("ur1wfgKFx2fqkRmtITFr2pJGiA82", "dddddddddddddddddddddd"))
# print(manager.get_users_to_show("bbbbbbbbbbbbbbbbbbbbbbbbb"))
# client = CouchbaseClient("conf/private_data.pb.txt")

# print(client.get_reactions_from("bej5dc9v65hWmw1DnRTeh4kkbIq2", False))
# print(client.get_reactions_to("bej5dc9v65hWmw1DnRTeh4kkbIq2", False))
# print(client.get_reactions("bbbbbbbbbbbbbbbbbbbbbbbbb", ["aaaaaaaaaaaaaaaaaaaaaaaaa", "cccccccccccccccccccccccc"]))
# aaaaaaaaaaaaaaaaaaaaaaaaa
# bbbbbbbbbbbbbbbbbbbbbbbbb
# cccccccccccccccccccccccc
# dddddddddddddddddddddd
# print(client.get_chats("OVpUsWkBlbcQyak9SyAOe27up1k2"))
