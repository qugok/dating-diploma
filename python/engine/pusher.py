import generated.event_pb2 as event_pb2
from lib.queue_client.kafka_queue_client import QueueClient

import logging

logger = logging.getLogger("engine")


class Pusher:
    def __init__(self, config):
        self.queue_client = QueueClient(config.QueueClientConfig)

    def send_messages(self, messages):
        event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_MESSAGE, Messages=messages)
        self.queue_client.write_to("processor_queue", event.SerializeToString())

    def send_reactions(self, reactions):
        event = event_pb2.TEvent(Type=event_pb2.EET_SEND_PUSH_REACTION, Reactions=reactions)
        self.queue_client.write_to("processor_queue", event.SerializeToString())

