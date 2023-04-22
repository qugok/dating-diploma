import logging
import time

from lib.config import read_config_from

from concurrent import futures
import generated.config_pb2 as config_pb2
import generated.event_pb2 as event_pb2
import traceback

from google.protobuf import text_format

from lib.tools.parse_args import congifure_parser
from lib.queue_client.kafka_queue_client import QueueClient

from processor.handler import Handler

logger = logging.getLogger("processor")
logger.setLevel(logging.DEBUG)

def server(config):
    client = QueueClient(config.QueueClientConfig)
    logger.info("Server started")
    handler = Handler(config)
    for msg in client.read_queue():
        event = event_pb2.TEvent()
        event.ParseFromString(msg.value)
        try:
            handler.HandleEvent(event)
        except Exception as e:
            logger.error(f"got exception {str(e) + str(traceback.format_exc())}")

if __name__ == '__main__':
    parser = congifure_parser()

    args = parser.parse_args()

    config = read_config_from(config_pb2.TProcessorConfig, args.config_folder + "/processor_config.pb.txt")

    logging.basicConfig(filename=args.log_path, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)

    logger.info("Starting Processor Server...")
    server(config)
    logger.info("Shutdown Processor Server.")

