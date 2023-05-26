import generated.user_pb2 as user_pb2
import generated.event_pb2 as event_pb2
import generated.config_pb2 as config_pb2
from lib.queue_client.kafka_queue_client import QueueClient

from lib.redis.client import RedisClient

import logging

logger = logging.getLogger("engine")


class Pusher:
    def __init__(self, config:config_pb2.TEngineConfig):
        self.queue_client = QueueClient(config.QueueClientConfig)
        self.redis = RedisClient(config.PrivateDataPath)

    def send_cool_down_messages_request(self, UID1:str, UID2:str):
        event = event_pb2.TEvent(Type=event_pb2.EET_COOL_DOWN_MESSAGES, UID1=UID1, UID2=UID2)
        self.queue_client.write_to("processor_queue", event.SerializeToString())

    def send_messages(self, messages):
        shard = self.redis.get_current_shard(messages[0].ToUID)
        logger.debug(f"got shard: {shard} for UID: {messages[0].ToUID}")
        if shard is not None:
            stream_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_STREAM_MESSAGE, Messages=messages)
            self.queue_client.write_to("streaming_queue", stream_event.SerializeToString(), shard)
        else:
            push_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_MESSAGE, Messages=messages)
            self.queue_client.write_to("processor_queue", push_event.SerializeToString())

    def send_reactions(self, reactions):
        shard = self.redis.get_current_shard(reactions[0].ToUID)
        logger.debug(f"got shard: {shard} for UID: {reactions[0].ToUID}")
        if shard is not None:
            stream_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_STREAM_REACTION, Reactions=reactions)
            self.queue_client.write_to("streaming_queue", stream_event.SerializeToString())
        else:
            push_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_REACTION, Reactions=reactions)
            self.queue_client.write_to("processor_queue", push_event.SerializeToString())

