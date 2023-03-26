import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import generated.config_pb2 as config_pb2

from lib.tools.decorators import process_simple_request
from lib.auth import FirebaseAuth
from media.media import MediaManager

import logging

logger = logging.getLogger(__name__)

class DatingMediaServer(dating_server_pb2_grpc.DatingServerServicer):
    # TODO научиться передавать ошибки не через поля, а в идеале и авторизацию

    def __init__(self, config:config_pb2.TServerConfig):
        super().__init__()
        self.auth = FirebaseAuth(config.Auth)

        self.logger = logger
        self.manager = MediaManager(config.PrivateDataPath)

    @process_simple_request(dating_server_pb2.UploadMediaReply)
    def UploadMedia(self, request:dating_server_pb2.UploadMediaRequest, context, user_auth_info):
        return {"Media": self.manager.upload_media(request.Media)}

    @process_simple_request(dating_server_pb2.DownloadMediaReply)
    def DownloadMedia(self, request:dating_server_pb2.DownloadMediaRequest, context, user_auth_info):
        return {"Media": self.manager.download_media(request.Media)}
