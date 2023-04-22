from aiokafka import AIOKafkaProducer
from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context
import ssl
from generated.config_pb2 import TQueueClientConfig


class AIOQueueClient:
    def __init__(self, config:TQueueClientConfig):
        context = create_ssl_context(cafile="/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt")

        args = {
            "bootstrap_servers": ['rc1a-itvja874bn7p94mb.mdb.yandexcloud.net:9091'],
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "SCRAM-SHA-512",
            "sasl_plain_username": f'{config.UserName}_client',
            "sasl_plain_password": f'{config.UserName}_client',
            "ssl_context": context
        }
        self.producer = AIOKafkaProducer(**args)
        self.consumer = AIOKafkaConsumer(f'{config.UserName}_queue', **args)

        self.topic_mapping = {}
        for mapping in config.TopicMapping:
            self.topic_mapping[mapping.From] = mapping.To

    async def start(self):
        await self.producer.start()
        await self.consumer.start()

    async def stop(self):
        await self.producer.stop()
        await self.consumer.stop()



    async def write_to(self, topic:str, message:str, key:str=None, flush=True):
        # Возможное место ускорения - подумать зо замене send_and_wait на send или send_batch
        real_topic = topic if topic not in self.topic_mapping else self.topic_mapping[topic]
        await self.producer.send_and_wait(real_topic, message, key)

    async def read_queue(self):
        async for msg in self.consumer:
            yield msg
