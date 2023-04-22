
# TODO обобщить
WORK_DIR="/home/diploma/dating-diploma"
RUN_DIR="$WORK_DIR/run"

export GOOGLE_APPLICATION_CREDENTIALS="$WORK_DIR/conf/sonder-dating-app-firebase-adminsdk-ww6qs-b0153cc5b8.json"

mkdir -p $RUN_DIR
mkdir -p $RUN_DIR/pids
mkdir -p $RUN_DIR/logs


function StopApp {
    app_name=$1
    if [ -f $RUN_DIR/pids/$app_name.pid ]; then
        kill `cat $RUN_DIR/pids/$app_name.pid`
    fi
}

function runApp {
        app_name=$1
        port=${2-0}
        port_param="--port $port"
        if [[ $port == 0 ]]; then
            port_param=""
        fi

        StopApp $app_name

        daemon  --name=$app_name \
        --pidfile=$RUN_DIR/pids/$app_name.pid \
        --chdir=$WORK_DIR \
        --unsafe --respawn --attempts=1 --delay=60 \
        --stdout=$RUN_DIR/logs/$app_name.out \
        --stderr=$RUN_DIR/logs/$app_name.err \
        -- python $WORK_DIR/python/$app_name/main.py \
        -c conf/dev \
        --log-path $RUN_DIR/logs/$app_name.log $port_param
}

runApp media 45000
runApp engine 45050
runApp processor
runApp streaming 45060

# daemon  --name="dating_server" \
#         --pidfile=$RUN_DIR/dating_server.pid \
#         --chdir=$WORK_DIR \
#         --unsafe --respawn --attempts=1 --delay=60 \
#         --stdout=$RUN_DIR/$APP_NAME.out \
#         --stderr=$RUN_DIR/$APP_NAME.err \
#         -- python $WORK_DIR/python/server.py
# # --output=$RUN_DIR/$APP_NAME.log \
