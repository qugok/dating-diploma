import logging
import time

from lib.config import read_config_from

from concurrent import futures
import grpc
import generated.config_pb2 as config_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc

from google.protobuf import text_format

from server import DatingServerEngine

from lib.tools.parse_args import congifure_parser

logger = logging.getLogger(__name__)

def server(port, config):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dating_server_pb2_grpc.add_DatingServerServicer_to_server(DatingServerEngine(config), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port, flush=True)
    logger.info("Server started, listening on " + port)
    server.wait_for_termination()

if __name__ == '__main__':
    parser = congifure_parser()

    args = parser.parse_args()
    print(time.localtime(), args.config_folder, args.log_path, args.port, flush=True)

    config = read_config_from(config_pb2.TServerConfig, args.config_folder + "/config.pb.txt")

    print(text_format.MessageToString(config, True))

    logging.basicConfig(filename=args.log_path, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)

    logger.info("Starting Engine Server...")
    server(args.port, config)
    logger.info("Shutdown Engine Server.")

