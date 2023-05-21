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


    def send_message(self, message:user_pb2.TMessage):
        shard = self.redis.get_current_shard(message.ToUID)
        logger.debug(f"got shard: {shard} for UID: {message.ToUID}")
        if shard is not None:
            stream_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_STREAM_MESSAGE, Messages=[message])
            self.queue_client.write_to("streaming_queue", stream_event.SerializeToString(), shard)
        else:
            push_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_MESSAGE, Messages=[message])
            self.queue_client.write_to("processor_queue", push_event.SerializeToString())


    def send_messages(self, messages):
        for message in messages:
            self.send_message(message)


    def send_reaction(self, reaction:user_pb2.TReaction):
        shard = self.redis.get_current_shard(reaction.ToUID)
        logger.debug(f"got shard: {shard} for UID: {reaction.ToUID}")
        if shard is not None:
            stream_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_STREAM_REACTION, Reactions=[reaction])
            self.queue_client.write_to("streaming_queue", stream_event.SerializeToString())
        else:
            push_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_REACTION, Reactions=[reaction])
            self.queue_client.write_to("processor_queue", push_event.SerializeToString())


    def send_reactions(self, reactions):
        for reaction in reactions:
            self.send_reaction(reaction)

