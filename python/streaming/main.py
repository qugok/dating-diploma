import asyncio
# import threading
import logging
import time

import sys
import traceback

from lib.config import read_config_from

from lib.queue_client.async_kafka_queue_client import AIOQueueClient
import grpc
import generated.config_pb2 as config_pb2
import generated.event_pb2 as event_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc

from google.protobuf import text_format

from streaming.server import StreamingDatingServer
from streaming.handler import Handler

from lib.tools.parse_args import congifure_parser

from lib.tools.proto_utils import FullMessageToDict

logger = logging.getLogger("streaming")
logger.setLevel(logging.DEBUG)

async def server(port, config):
    server = grpc.aio.server()
    session_holder = StreamingDatingServer(config)
    dating_server_pb2_grpc.add_DatingServerServicer_to_server(session_holder, server)
    server.add_insecure_port('[::]:' + port)
    await server.start()
    client = AIOQueueClient(config.QueueClientConfig)
    await client.start()

    print("Server started, listening on " + port, flush=True)
    logger.info("Server started, listening on " + port)
    handler = Handler(config, session_holder)
    async for msg in client.read_queue():
        event = event_pb2.TEvent()
        event.ParseFromString(msg.value)
        try:
            await handler.HandleEvent(event)
        except Exception as e:
            logger.error(f"got exception {str(e) + str(traceback.format_exc())}")

    await client.stop()

if __name__ == '__main__':
    parser = congifure_parser()

    args = parser.parse_args()

    config = read_config_from(config_pb2.TStreamingConfig, args.config_folder + "/streaming_config.pb.txt")

    logging.basicConfig(filename=args.log_path, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)

    logger.info("Starting Streaming Server...")
    asyncio.run(server(args.port, config))
    logger.info("Shutdown Streaming Server.")

