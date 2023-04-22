import generated.event_pb2 as event_pb2
import generated.config_pb2 as config_pb2
import generated.dating_server_pb2 as dating_server_pb2
from streaming.server import StreamingDatingServer
from lib.request.wrapper import SetErrorReply, SetOkReplyStatus
from lib.queue_client.event_handler_base import HandlerBase
import logging
from lib.tools.proto_utils import FullMessageToDict

logger = logging.getLogger("streaming")

class Handler(HandlerBase):
    def __init__(self, config : config_pb2.TStreamingConfig, session_holder:StreamingDatingServer) -> None:
        super().__init__()
        self.sessin_holder = session_holder

        self.RegisterHandler(event_pb2.EET_SEND_STREAM_MESSAGE, self.SendMessage)
        self.RegisterHandler(event_pb2.EET_SEND_STREAM_REACTION, self.SendReaction)

    def RegisterHandler(self, event_type:event_pb2.EEventType, handler):
        self.handlers[event_type] = handler

    async def HandleEvent(self, event: event_pb2.TEvent):
        if event.Type not in self.handlers:
            logger.error(f"there is no handler for event type: {event.Type}")
            return
        await self.handlers[event.Type](event)


    async def SendMessage(self, event: event_pb2.TEvent):
        if len(event.Messages) == 0:
            logger.error(f"got empty push message event: {FullMessageToDict(event)}")
            return
        logger.info(f"got send message event: {FullMessageToDict(event)}")

        for message in event.Messages:
            reply = dating_server_pb2.GetUpdatesReply(Messages=[message])
            await self.sessin_holder.send_update(message.ToUID, SetOkReplyStatus(reply))


    async def SendReaction(self, event: event_pb2.TEvent):
        if len(event.Reactions) == 0:
            logger.info(f"got empty send reaction event: {FullMessageToDict(event)}")
            return
        logger.info(f"got send reaction event: {FullMessageToDict(event)}")

        for reaction in event.Reactions:
            reply = dating_server_pb2.GetUpdatesReply(Reactions=[reaction])
            await self.sessin_holder.send_update(reaction.ToUID, SetOkReplyStatus(reply))

