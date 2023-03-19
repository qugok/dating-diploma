
# TODO обобщить
WORK_DIR="/home/diploma/dating-diploma"
RUN_DIR="$WORK_DIR/run"
APP_NAME="dating_server"

export GOOGLE_APPLICATION_CREDENTIALS="$WORK_DIR/sonder-dating-app-firebase-adminsdk-ww6qs-b0153cc5b8.json"

mkdir -p $RUN_DIR

daemon  --name="dating_server" \
        --pidfile=$RUN_DIR/dating_server.pid \
        --chdir=`pwd` \
        --unsafe --respawn --attempts=1 --delay=60 \
        --stdout=$RUN_DIR/$APP_NAME.out \
        --stderr=$RUN_DIR/$APP_NAME.err \
        -- python $WORK_DIR/python/server.py
# --output=$RUN_DIR/$APP_NAME.log \
