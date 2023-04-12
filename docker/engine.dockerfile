FROM python:3.9

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install pyopenssl
RUN pip install grpcio
RUN pip install grpcio-tools
RUN pip install couchbase==4.1.2

RUN pip install uuid
RUN pip install firebase-admin


RUN apt-get install make

ADD protos protos
ADD python/generated/__init__.py python/generated/__init__.py
ADD Makefile Makefile

RUN make

ADD python/engine/* python/engine/
ADD python/lib python/lib
ADD conf conf

ENV GOOGLE_APPLICATION_CREDENTIALS="$/conf/sonder-dating-app-firebase-adminsdk-ww6qs-b0153cc5b8.json"
ENV PYTHONPATH=/python:$PYTHONPATH

CMD python python/engine/main.py -c conf --port 20000

EXPOSE 20000
