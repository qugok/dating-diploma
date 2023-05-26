import generated.user_pb2 as user_pb2
from lib.yandex_s3.client import YandexObjectStorageClient
from lib.exceptions import WrongRequest

import uuid

import logging
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger("media")

def get_path_prefix(m_type: user_pb2.EMediaType):
    if m_type == user_pb2.EMT_AUDIO:
        return "audio"
    elif m_type == user_pb2.EMT_PHOTO:
        return "photo"
    elif m_type == user_pb2.EMT_VIDEO:
        return "video"

class MediaManager:
    def __init__(self):
        # TODO добавить отдельный конфиг для менеджера
        self.client = YandexObjectStorageClient()

    def upload_media(self, media:user_pb2.TLoadingMedia):
        if media.LoadType != user_pb2.TLoadingMedia.ELT_FULL:
            raise WrongRequest(f"supported only ELT_FULL not {media.LoadType}")
        prefix = get_path_prefix(media.Type)
        if not prefix:
            raise WrongRequest(f"dont supported media type: {media.Type}")
        random_id = uuid.uuid4()
        path = f"{prefix}/{random_id}"
        self.client.write_media(path, media.Data)
        return user_pb2.TMetaMedia(Type=media.Type, Path=path)

    def download_media(self, media:user_pb2.TMetaMedia):
        prefix = get_path_prefix(media.Type)
        if not media.Path or not media.Path.startswith(prefix):
            raise WrongRequest(f"media type dont match to path prefix")

        data = self.client.read_media(media.Path)
        return user_pb2.TLoadingMedia(
            Type=media.Type,
            LoadType=user_pb2.TLoadingMedia.ELT_FULL,
            Path=media.Path,
            Data=data,
        )

