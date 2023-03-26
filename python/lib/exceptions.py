from generated.misc_pb2 import TErrorInfo

class DatingServerException(BaseException):
    e_type = TErrorInfo.EET_INTERNAL
    pass

class UserDontExist(DatingServerException):
    e_type = TErrorInfo.EET_USER_DONT_REGISTERED
    def __str__(self) -> str:
        return "User don't registered"

class MethodDontSupported(DatingServerException):
    # TODO поменять на unsupported method
    e_type = TErrorInfo.EET_INTERNAL
    def __init__(self, message:str):
        self.message = message

    def __str__(self) -> str:
        return f"method dont supported: {self.message}"

class WrongRequest(DatingServerException):
    # TODO поменять на unsupported method
    e_type = TErrorInfo.EET_INTERNAL
    def __init__(self, message:str):
        self.message = message

    def __str__(self) -> str:
        return f"wrong request: {self.message}"
