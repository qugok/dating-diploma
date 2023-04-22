import generated.event_pb2 as event_pb2
from lib.queue_client.kafka_queue_client import QueueClient

import logging

logger = logging.getLogger("engine")


class Pusher:
    def __init__(self, config):
        self.queue_client = QueueClient(config.QueueClientConfig)

    def send_messages(self, messages):
        push_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_MESSAGE, Messages=messages)
        stream_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_STREAM_MESSAGE, Messages=messages)
        self.queue_client.write_to("processor_queue", push_event.SerializeToString())
        self.queue_client.write_to("streaming_queue", stream_event.SerializeToString())

    def send_reactions(self, reactions):
        push_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_REACTION, Reactions=reactions)
        stream_event = event_pb2.TEvent(Type=event_pb2.EET_SEND_STREAM_REACTION, Reactions=reactions)
        self.queue_client.write_to("processor_queue", push_event.SerializeToString())
        self.queue_client.write_to("streaming_queue", stream_event.SerializeToString())

