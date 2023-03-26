
# TODO обобщить
WORK_DIR="/home/diploma/dating-diploma"
RUN_DIR="$WORK_DIR/run"

export GOOGLE_APPLICATION_CREDENTIALS="$WORK_DIR/conf/sonder-dating-app-firebase-adminsdk-ww6qs-b0153cc5b8.json"

mkdir -p $RUN_DIR


function StopApp {
    app_name=$1
    if [ -f $RUN_DIR/$app_name.pid ]; then
        kill `cat $RUN_DIR/$app_name.pid`
    fi
}

function runApp {
        app_name=$1
        port=$2

        StopApp $app_name

        daemon  --name=$app_name \
        --pidfile=$RUN_DIR/$app_name.pid \
        --chdir=$WORK_DIR \
        --unsafe --respawn --attempts=1 --delay=60 \
        --stdout=$RUN_DIR/$app_name.out \
        --stderr=$RUN_DIR/$app_name.err \
        -- python $WORK_DIR/python/$app_name/main.py \
        -c conf \
        --log-path $RUN_DIR/$app_name.log \
        --port $port
}

# runApp media 45000
runApp engine 45050

# daemon  --name="dating_server" \
#         --pidfile=$RUN_DIR/dating_server.pid \
#         --chdir=$WORK_DIR \
#         --unsafe --respawn --attempts=1 --delay=60 \
#         --stdout=$RUN_DIR/$APP_NAME.out \
#         --stderr=$RUN_DIR/$APP_NAME.err \
#         -- python $WORK_DIR/python/server.py
# # --output=$RUN_DIR/$APP_NAME.log \
