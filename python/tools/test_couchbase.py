from lib.couchbase.client import CouchbaseClient



client = CouchbaseClient("conf/private_data.pb.txt")

# print(client.get_reactions_from("bej5dc9v65hWmw1DnRTeh4kkbIq2", False))
# print(client.get_reactions_to("bej5dc9v65hWmw1DnRTeh4kkbIq2", False))
# print(client.get_reactions("bbbbbbbbbbbbbbbbbbbbbbbbb", ["aaaaaaaaaaaaaaaaaaaaaaaaa", "cccccccccccccccccccccccc"]))
# print(client.read_hot_messages("ur1wfgKFx2fqkRmtITFr2pJGiA82", "dddddddddddddddddddddd"))
print(client.hot_messages_count("ur1wfgKFx2fqkRmtITFr2pJGiA82", "dddddddddddddddddddddd"))
# print(client.move_messages_to_cold(["298fd0fb-95fc-4318-897e-3db813a292f3", "ur1wfgKFx2fqkRmtITFr2pJGiA82", "734b88d3-9dca-44c9-b98d-41606d0ec700"]))



# print(client.get_chats("OVpUsWkBlbcQyak9SyAOe27up1k2"))
