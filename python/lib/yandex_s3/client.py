import boto3

# import io

class YandexObjectStorageClient:

    def __init__(self):
        self.session = boto3.session.Session()
        self.s3 = self.session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net'
        )
        self.bucket_name = "dating-media"

    # TODO научиться скачивать о отдавать файл частями для ELT_BY_PART
    def read_media(self, path:str):
        get_object_response = self.s3.get_object(Bucket=self.bucket_name,Key=path)
        return get_object_response['Body'].read()

    def write_media(self, path: str, data):
        self.s3.put_object(Bucket=self.bucket_name, Key=path, Body=data, StorageClass='STANDARD')
