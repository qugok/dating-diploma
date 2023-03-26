
# TODO обобщить
WORK_DIR="/home/diploma/dating-diploma"
RUN_DIR="$WORK_DIR/run"
APP_NAME="dating_server"

function StopApp {
    app_name=$1
    kill `cat $RUN_DIR/$app_name.pid`
}

# StopApp media
StopApp engine
