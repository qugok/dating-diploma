import firebase_admin
from firebase_admin import auth as firebase_auth
from generated.misc_pb2 import TAuth
import generated.config_pb2 as config_pb2

# app = firebase_admin.initialize_app()


class UserAuthInfo() :
    def __init__(self, decoded_token):
        self.uid = decoded_token['uid']
        # TODO etc

class FirebaseAuth():
    # TODO обобщить до FirebaseApp
    # TODO разделить авторизацию и аутентификацию

    def __init__(self, config:config_pb2.TAuthConfig):
        # self.enabled = config.Enabled
        self.app = firebase_admin.initialize_app()
        self.enabled = False
        pass

    def get_user_auth_info(self, auth: TAuth):
        if not auth or not auth.Token:
            fake_decoded_token = {'uid':None}
            return UserAuthInfo(fake_decoded_token)

        decoded_token = firebase_auth.verify_id_token(auth.Token)
        print("got token while verification:")
        print(decoded_token)
        return UserAuthInfo(decoded_token)

    def authorize_user(self, user_auth_info: UserAuthInfo, request_name, request):
        if not self.enabled:
            return True

