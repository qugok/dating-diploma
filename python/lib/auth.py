import firebase_admin
from firebase_admin import auth as firebase_auth
from generated.misc_pb2 import TAuth
import generated.config_pb2 as config_pb2

# app = firebase_admin.initialize_app()

from firebase_admin import messaging
import logging

logger = logging.getLogger("lib")

class UserAuthInfo() :
    def __init__(self, decoded_token):
        self.uid = decoded_token['uid']
        # TODO etc

class FirebaseApp():
    # TODO разделить авторизацию и аутентификацию

    def __init__(self, config:config_pb2.TAuthConfig):
        self.enabled = config.Enabled
        logger.debug(f"FirebaseApp.config.Enabled: {config.Enabled}")
        self.app = firebase_admin.initialize_app()
        self.logged_in_users = {}

    def authenticate_user(self, auth):
        if not self.enabled:
            return UserAuthInfo({'uid':''})

        if not auth or not auth.Token:
            return None
        user_info = self.get_user_auth_info(auth)
        if user_info.uid not in self.logged_in_users:
            self.logged_in_users[user_info.uid] = (auth.Token, user_info)
        return self.logged_in_users[user_info.uid][1]

    def get_user_auth_info(self, auth: TAuth):
        decoded_token = firebase_auth.verify_id_token(auth.Token)
        logger.debug(f"got token while verification: {decoded_token} real token: {auth.Token}")
        return UserAuthInfo(decoded_token)

    def authorize_user(self, user_auth_info: UserAuthInfo, request_name, request):
        if not self.enabled:
            return True

    def send_user_push(self, UID:str, title, body):
        if UID not in self.logged_in_users:
            return False
        token, _ = self.logged_in_users[UID]
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )
        messaging.send(message)
