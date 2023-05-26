from kafka import KafkaConsumer

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename=None, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', force=True)


consumer = KafkaConsumer(
    'processor',
    bootstrap_servers=['rc1a-itvja874bn7p94mb.mdb.yandexcloud.net:9091'],
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username='processor_client',
    sasl_plain_password='processor_client',
    ssl_cafile="/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt")

print("ready")

for msg in consumer:
    print(msg.key.decode("utf-8") + ":" + msg.value.decode("utf-8"))
