import generated.user_pb2 as user_pb2
import generated.dating_server_pb2 as dating_server_pb2
from google.protobuf import text_format


# s TODO переделать валидацию на возвращающую true или false и обрабатывать её без проброса ошибок

def validate_user(user: user_pb2.TUser):
    if not (user.UID and user.Name and user.Description):
        raise Exception("Invalid User")

def validate_UID(UID: str):
    return UID is not None

def validate_set_reaction(request: dating_server_pb2.SetReactionRequest):
    if not (validate_UID(request.FromUID) and validate_UID(request.ToUID) and request.Reaction):
        raise Exception("Invalid Set Reaction Request")

