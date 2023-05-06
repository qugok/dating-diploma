FROM python:3.9

RUN apt-get update

RUN apt-get install -y libsnappy-dev

RUN pip install --upgrade pip
RUN pip install pyopenssl
RUN pip install grpcio
RUN pip install grpcio-tools
RUN pip install asyncio
RUN pip install aiokafka
RUN pip install firebase-admin

RUN pip install kafka-python lz4 python-snappy crc32c

RUN apt-get install -y make

ADD protos protos
ADD python/generated/__init__.py python/generated/__init__.py
ADD Makefile Makefile

RUN make

ADD python/streaming/* python/streaming/
ADD python/lib python/lib
ADD conf conf

# for kafka
RUN mkdir --parents /usr/local/share/ca-certificates/Yandex
RUN wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" --output-document /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt
RUN chmod 655 /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt

#for firebase auth
ENV GOOGLE_APPLICATION_CREDENTIALS="/conf/sonder-dating-app-firebase-adminsdk-ww6qs-b0153cc5b8.json"
ENV PYTHONPATH=/python:$PYTHONPATH

CMD python python/streaming/main.py -c conf/prod --port 20000

EXPOSE 20000
