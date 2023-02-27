import generated.user_pb2 as user_pb2
from google.protobuf import text_format


def DefaultUser():
    user = user_pb2.TUser(UID="ardgsehgses", Name="Alex", Descripton="ай, выхади за меня дарагая, лучшый парень ever!")
    return user

def SerializeUser(user: user_pb2.TUser):
    return text_format.MessageToString(user)

def ParseUser(user_str: str):
    user = user_pb2.TUser()
    text_format.Parse(user_str, user)
    return user
