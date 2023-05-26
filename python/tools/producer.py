from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['rc1a-itvja874bn7p94mb.mdb.yandexcloud.net:9091'],
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_username='engine_client',
    sasl_plain_password='engine_client',
    ssl_cafile="/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt")

producer.send('processor_queue', b'test message', b'key')
producer.flush()
producer.close()
