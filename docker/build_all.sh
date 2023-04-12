REGISTRY_ID="crpmht6s4vkhnj1pe05c"


# sudo docker run -p 20000:20000 python-engine


BASE_DIR=$( dirname  $( dirname  `readlink -f $0`))
cd $BASE_DIR

sudo docker build -f docker/engine.dockerfile -t cr.yandex/$REGISTRY_ID/python-engine .

sudo docker push cr.yandex/$REGISTRY_ID/python-engine

sudo docker build -f docker/media.dockerfile -t cr.yandex/$REGISTRY_ID/python-media .

sudo docker push cr.yandex/$REGISTRY_ID/python-media
