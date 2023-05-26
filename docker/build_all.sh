REGISTRY_ID="crpmht6s4vkhnj1pe05c"

VERSION="0.2.02"


BASE_DIR=$( dirname  $( dirname  `readlink -f $0`))
cd $BASE_DIR

# sudo docker build -f docker/engine.dockerfile -t cr.yandex/$REGISTRY_ID/python-engine:$VERSION .

# sudo docker push cr.yandex/$REGISTRY_ID/python-engine:$VERSION

# sudo docker build -f docker/media.dockerfile -t cr.yandex/$REGISTRY_ID/python-media:$VERSION .

# sudo docker push cr.yandex/$REGISTRY_ID/python-media:$VERSION

sudo docker build -f docker/processor.dockerfile -t cr.yandex/$REGISTRY_ID/python-processor:$VERSION .

sudo docker push cr.yandex/$REGISTRY_ID/python-processor:$VERSION

# sudo docker build -f docker/streaming.dockerfile -t cr.yandex/$REGISTRY_ID/python-streaming:$VERSION .

# sudo docker push cr.yandex/$REGISTRY_ID/python-streaming:$VERSION
