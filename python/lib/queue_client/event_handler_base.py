import generated.event_pb2 as event_pb2
import logging
from lib.tools.proto_utils import FullMessageToDict
logger = logging.getLogger("lib")

class HandlerBase:
    def __init__(self) -> None:
        self.handlers = {}

    def RegisterHandler(self, event_type:event_pb2.EEventType, handler):
        logger.debug(f"register handler for {event_type}")
        self.handlers[event_type] = handler

    def HandleEvent(self, event: event_pb2.TEvent):
        logger.debug(f"handlig event {FullMessageToDict(event)}")
        if event.Type not in self.handlers:
            logger.error(f"there is no handler for event type: {event.Type}")
            return
        logger.debug(f"handlig event by {self.handlers[event.Type]}")
        self.handlers[event.Type](event)
        logger.debug(f"handled event")
