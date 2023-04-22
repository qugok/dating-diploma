
import asyncio
from collections import defaultdict
# import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import generated.misc_pb2 as misc_pb2

from lib.tools.proto_utils import FullMessageToDict

from lib.tools.decorators import process_simple_request
# from lib.auth import FirebaseApp
from lib.validate_request import Validator
# from engine.manager import Manager
import traceback
import logging

logger = logging.getLogger("streaming")

class StreamingDatingServer(dating_server_pb2_grpc.DatingServerServicer):
    # TODO научиться передавать ошибки не через поля, а в идеале и авторизацию

    def __init__(self, config):
        super().__init__()
        self.validator = Validator()
        self.sessions = defaultdict(list)
        self.sessions_lock = asyncio.Lock()

    async def send_update(self, UID:str, reply:dating_server_pb2.GetUpdatesReply):
        logger.debug(f"send_update for UID: {UID} and reply: {FullMessageToDict(reply)}")
        async with self.sessions_lock:
            if UID not in self.sessions:
                logger.info(f"there is no session for UID: {UID}")
                return
            for session in self.sessions[UID]:
                logger.debug(f"sending messgae to single session")
                session.put_nowait(reply)

    async def GetUpdates(self, request:dating_server_pb2.GetUpdatesRequest, context):
        logger.info(f"Got GetUpdates request: {FullMessageToDict(request)}")
        rsp = dating_server_pb2.GetUpdatesReply(Status=misc_pb2.ERS_OK)
        yield rsp
        responce_queue = asyncio.Queue()
        async with self.sessions_lock:
            self.sessions[request.UID].append(responce_queue)
        logger.info(f"start GetUpdates waiting for {request.UID}")
        try:
            while True:
                new_item = await responce_queue.get()
                logger.debug(f"sending for UID:{request.UID} event: {FullMessageToDict(new_item)}")
                yield new_item
                logger.debug(f"waiting ro new responce for UID:{request.UID}")
        except Exception as e:
            logger.error(f"got exception {str(e) + str(traceback.format_exc())}")


