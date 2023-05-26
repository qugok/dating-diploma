
import asyncio
from collections import defaultdict
# import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import generated.misc_pb2 as misc_pb2
import generated.config_pb2 as config_pb2

from lib.tools.proto_utils import FullMessageToDict

from lib.tools.decorators import process_simple_request
# from lib.auth import FirebaseApp
from lib.validate_request import Validator
from lib.auth import FirebaseApp
from lib.request.wrapper import SetErrorReply, SetOkReplyStatus
from lib.redis.client import RedisClient
# from engine.manager import Manager
import traceback
import logging

logger = logging.getLogger("streaming")

class StreamingDatingServer(dating_server_pb2_grpc.DatingServerServicer):
    # TODO научиться передавать ошибки не через поля, а в идеале и авторизацию

    def __init__(self, config: config_pb2.TStreamingConfig, shard):
        super().__init__()
        self.shard = shard
        self.validator = Validator()
        self.sessions = dict()
        self.sessions_lock = asyncio.Lock()
        self.redis = RedisClient(config.PrivateDataPath)
        self.auth = FirebaseApp(config.Auth)

    async def send_update(self, UID:str, reply:dating_server_pb2.GetUpdatesReply):
        logger.debug(f"send_update for UID: {UID} and reply: {FullMessageToDict(reply)}")
        async with self.sessions_lock:
            if UID not in self.sessions:
                logger.info(f"there is no session for UID: {UID}")
                return
            session = self.sessions[UID]
            logger.debug(f"sending messgae to single session")
            session.put_nowait(reply)

    async def GetUpdates(self, request:dating_server_pb2.GetUpdatesRequest, context):
        logger.info(f"Got GetUpdates request: {FullMessageToDict(request)}")
        user_auth_info = self.auth.authenticate_user(request.Auth)
        logger.debug(f"authentication got user_auth_info: {user_auth_info}")
        if user_auth_info is None:
            logger.debug(f"ErrorReply: authentication user_auth_info: {user_auth_info}")
            yield SetErrorReply(
                dating_server_pb2.GetUpdatesReply(),
                f"authentication error for user auth {FullMessageToDict(request.Auth)}",
                misc_pb2.TErrorInfo.EET_AUTHORIZATION
            )
            return

        if request.UID:
            yield SetOkReplyStatus(dating_server_pb2.GetUpdatesReply())
        else:
            yield SetErrorReply(
                    dating_server_pb2.GetUpdatesReply(),
                    "request shuld have uid",
                    misc_pb2.TErrorInfo.EET_BAD_REQUEST
                )
            return


        response_queue = asyncio.Queue()
        async with self.sessions_lock:
            if request.UID in self.sessions:
                await self.sessions[request.UID].put(None)
            self.sessions[request.UID] = response_queue
            self.redis.register_session(request.UID, self.shard)
        logger.info(f"start GetUpdates waiting for {request.UID}")
        try:
            while True:
                new_item = await response_queue.get()
                if new_item is None:
                    return
                logger.debug(f"sending for UID:{request.UID} event: {FullMessageToDict(new_item)}")
                yield new_item
                logger.debug(f"waiting ro new response for UID:{request.UID}")
        except Exception as e:
            logger.error(f"got exception {str(e) + str(traceback.format_exc())}")
        # except asyncio.CancelledError as e:
        #     logger.error(f"conncection UID:{request.UID} canceled: {str(e)}")
        except:
            logger.error(f"conncection UID:{request.UID} canceled")
        finally:
            async with self.sessions_lock:
                self.sessions.pop(request.UID)
            self.redis.end_session(request.UID, self.shard)



