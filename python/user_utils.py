import generated.user_pb2 as user_pb2
from google.protobuf import text_format


def DefaultUser():
    key = user_pb2.TUserKey(Hash=4567890987)
    user = user_pb2.TUser(Key=key, Name="Alex", Descripton="ай, выхади за меня дарагая, лучшый парень ever!")
    return user


def KeyToString(key: user_pb2.TUserKey):
    return f"Hash: {key.Hash}"

def UserToString(user: user_pb2.TUser):
    return f"User \"{user.Name}\" with Key: {KeyToString(user.Key)}\n" \
            f"Has {len(user.Photos)} Photos\n" \
            f"And Description: \"{user.Descripton}\""


def SerializeUser(user: user_pb2.TUser):
    return text_format.MessageToString(user)

def ParseUser(user_str: str):
    user = user_pb2.TUser()
    text_format.Parse(user_str, user)
    return user
