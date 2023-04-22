import generated.event_pb2 as event_pb2
import generated.config_pb2 as config_pb2
import generated.user_pb2 as user_pb2
from lib.auth import FirebaseApp
from lib.couchbase.client import CouchbaseClient
from lib.queue_client.event_handler_base import HandlerBase
import logging

logger = logging.getLogger("processor")

class Handler(HandlerBase):
    def __init__(self, config : config_pb2.TProcessorConfig) -> None:
        super().__init__()
        self.fapp = FirebaseApp(config.Auth)
        self.cbclient = CouchbaseClient(config.PrivateDataPath)

        self.RegisterHandler(event_pb2.EET_SEND_PUSH_MESSAGE, self.PushMessage)
        self.RegisterHandler(event_pb2.EET_SEND_PUSH_REACTION, self.PushReaction)

    def PushMessage(self, event: event_pb2.TEvent):
        if len(event.Messages) == 0:
            logger.error(f"got empty push message event: {event}")
            return
        logger.info(f"got push message event: {event}")

        for message in event.Messages:
            if not self.cbclient.has_message_token(message.ToUID):
                logger.error(f"don't know message token: {message}")
                continue
            token = self.cbclient.get_message_token(message.ToUID)
            logger.debug(f"found token: {token}")

            user = self.cbclient.get_user(message.FromUID)
            title = f"Сообщение от {user.Name}"

            self.fapp.send_user_push(token, title, message.Text)


    def PushReaction(self, event: event_pb2.TEvent):
        if len(event.Reactions) == 0:
            logger.info(f"got empty push reaction event: {event}")
            return
        logger.info(f"got push reaction event: {event}")

        for reaction in event.Reactions:
            if not self.cbclient.has_message_token(reaction.ToUID):
                logger.error(f"don't know message token: {reaction}")
                continue

            token = self.cbclient.get_message_token(reaction.ToUID)
            logger.debug(f"found token: {token}")

            user = self.cbclient.get_user(reaction.FromUID)
            react = "Лайк" if reaction.ReactionType == user_pb2.TReaction.ERT_LIKE else "Дизлайк"
            title = f"{react} от {user.Name}"

            body = ""

            self.fapp.send_user_push(token, title, body)

