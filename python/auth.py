import firebase_admin
from firebase_admin import auth

# app = firebase_admin.initialize_app()


class UserAuthInfo() :
    def __init__(self, decoded_token):
        self.uid = decoded_token['uid']
        # TODO etc

class FirebaseAuth() :

    def __init__(self):
        pass

    def get_user_auth_info(self, token):
        decoded_token = auth.verify_id_token(token)
        print("got token while verification:")
        print(decoded_token)
        return UserAuthInfo(decoded_token)

