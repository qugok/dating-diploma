import generated.event_pb2 as event_pb2
import generated.config_pb2 as config_pb2
import generated.user_pb2 as user_pb2
from lib.auth import FirebaseApp
from lib.couchbase.client import CouchbaseClient
from lib.queue_client.event_handler_base import HandlerBase
from lib.consts import INFINITY, HOT_MESSAGES_COUNT_AFTER_COOL_DOWN, MAX_POSSIBLY_HOT_MESSAGES_COUNT
import logging

logger = logging.getLogger("processor")

class Handler(HandlerBase):
    def __init__(self, config : config_pb2.TProcessorConfig) -> None:
        super().__init__()
        self.fapp = FirebaseApp(config.Auth)
        self.cbclient = CouchbaseClient(config.PrivateDataPath)

        self.RegisterHandler(event_pb2.EET_SEND_PUSH_MESSAGE, self.PushMessage)
        self.RegisterHandler(event_pb2.EET_SEND_PUSH_REACTION, self.PushReaction)
        self.RegisterHandler(event_pb2.EET_COOL_DOWN_MESSAGES, self.CoolDownMessages)

    #TODO отправлять все реакции и сообщения в одном ивенте, т.к теперь есть гарантия, что они все от одного конкретного пользователя к другому
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

            body = title

            self.fapp.send_user_push(token, title, body)

    def CoolDownMessages(self, event: event_pb2.TEvent):
        uid1, uid2 = event.UID1, event.UID2
        hot_messages = self.cbclient.read_hot_messages(uid1, uid2, limit=INFINITY, return_keys=True)
        logger.debug(f"got {len(hot_messages)} hot messages")
        if len(hot_messages) < MAX_POSSIBLY_HOT_MESSAGES_COUNT * 0.95:
            logger.debug(f"not enough hot messages: {len(hot_messages)} < {MAX_POSSIBLY_HOT_MESSAGES_COUNT}")
            return
        keys_to_cool_down = [key for key, m in hot_messages[HOT_MESSAGES_COUNT_AFTER_COOL_DOWN:]]
        logger.debug(f"cooling down {len(keys_to_cool_down)} hot messages")
        self.cbclient.move_messages_to_cold(keys_to_cool_down)

