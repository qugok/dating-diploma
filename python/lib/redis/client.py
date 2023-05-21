from rediscluster import RedisCluster
import logging

import generated.config_pb2 as config_pb2
from lib.config import read_config_from
import json
import datetime

class RedisClient:


    def __init__(self, config_path) -> None:
        configs = read_config_from(config_pb2.TPrivateData, config_path)
        startup_nodes = [{"host": configs.RedisHost, "port": configs.RedisPort}]

        self.redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=True, password=configs.RedisPassword)

    def register_session(self, UID:str, shard:int):
        now = datetime.datetime.now()

        self.redis.hset('sessions',
            UID, json.dumps(
             {"shard": shard,
              "start_time": str(now),
              "end_time": None}
              ))

    def end_session(self, UID:str, shard:int):
        if not self.redis.hexists('sessions', UID):
            return
        session = json.loads(self.redis.hget('sessions', UID))
        if session['shard'] == shard:
            now = datetime.datetime.now()
            session['end_time'] = str(now)
            self.redis.hset('sessions', UID, json.dumps(session))

    def get_current_shard(self, UID:str):
        if not self.redis.hexists('sessions', UID):
            return None
        session = json.loads(self.redis.hget('sessions', UID))
        if session["end_time"] is not None:
            return None
        return session["shard"]


