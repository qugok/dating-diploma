from lib.redis.client import RedisClient
import time

# from rediscluster import RedisCluster

# # pool = redis.ConnectionPool(host='10.112.131.27', port=6379, db=0)
# startup_nodes = [{"host": "10.112.131.27", "port": "6379"}]

# # redis = redis.Redis(connection_pool=pool, password="yorsHbcHwS")
# my_redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, password="yorsHbcHwS")

# my_redis.set('mykey', 'Hello from Python!')
# value = my_redis.get('mykey')
# print(value)

# my_redis.zadd('vehicles', {'car' : 0})
# my_redis.zadd('vehicles', {'bike' : 0})
# vehicles = my_redis.zrange('vehicles', 0, -1)
# print(vehicles)

client = RedisClient("conf/private_data.pb.txt")
client.register_session("qwertyuio", 4)

time.sleep(20)

client.end_session("qwertyuio", 4)
