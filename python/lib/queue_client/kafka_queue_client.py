from kafka import KafkaProducer
from kafka import KafkaConsumer

from generated.config_pb2 import TQueueClientConfig


class QueueClient:
    def __init__(self, config:TQueueClientConfig) -> None:
        args = {
            "bootstrap_servers": ['rc1a-itvja874bn7p94mb.mdb.yandexcloud.net:9091'],
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "SCRAM-SHA-512",
            "sasl_plain_username": f'{config.UserName}_client',
            "sasl_plain_password": f'{config.UserName}_client',
            "ssl_cafile": "/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt"
        }
        self.producer = KafkaProducer(**args)
        self.consumer = KafkaConsumer(f'{config.UserName}_queue', **args)
        self.topic_mapping = {}
        for mapping in config.TopicMapping:
            self.topic_mapping[mapping.From] = mapping.To

    def write_to(self, topic:str, message:str, shard:int=None, flush=True):
        real_topic = topic if topic not in self.topic_mapping else self.topic_mapping[topic]
        self.producer.send(real_topic, message, partition=shard)
        if flush:
            self.producer.flush()

    def flush(self):
        self.producer.flush()

    def read_queue(self):
        for msg in self.consumer:
            yield msg
