import generated.event_pb2 as event_pb2

import logging

logger = logging.getLogger("processor")

class Handler:
    def __init__(self) -> None:
        self.handlers = {}

        self.RegisterHandler(event_pb2.EET_SEND_PUSH_MESSAGE, self.PushMessage)
        self.RegisterHandler(event_pb2.EET_SEND_PUSH_REACTION, self.PushReaction)

    def RegisterHandler(self, event_type, handler):
        self.handlers[event_type] = handler

    def HandleEvent(self, event: event_pb2.TEvent):
        self.handlers[event.Type](event)

    def PushMessage(self, event: event_pb2.TEvent):
        logger.info(f"got push message event: {event}")

    def PushReaction(self, event: event_pb2.TEvent):
        logger.info(f"got push reaction event: {event}")

