from generated.misc_pb2 import TErrorInfo

class DatingServerException(BaseException):
    def __init__(self, *args: object) -> None:
        self.e_type = TErrorInfo.EET_INTERNAL

class UserDontExist(DatingServerException):

    def __init__(self, *args: object) -> None:
        self.e_type = TErrorInfo.EET_USER_DONT_REGISTERED
    def __str__(self) -> str:
        return "User don't registered"

class MethodDontSupported(DatingServerException):
    # TODO поменять на unsupported method

    def __init__(self, *args: object) -> None:
        self.e_type = TErrorInfo.EET_INTERNAL
    def __init__(self, message:str):
        self.message = message

    def __str__(self) -> str:
        return f"method dont supported: {self.message}"

class WrongRequest(DatingServerException):

    def __init__(self, message:str):
        self.message = message
        self.e_type = TErrorInfo.EET_INTERNAL

    def __str__(self) -> str:
        return f"wrong request: {self.message}"

class KeyDontExist(DatingServerException):

    def __init__(self, base:str, key:str, ) -> None:
        self.e_type = TErrorInfo.EET_INTERNAL
        self.base = base
        self.key = key
    def __str__(self) -> str:
        return f"Key \"{self.key}\" not found in base \"{self.base}\""


class KeyAlreadyExist(DatingServerException):

    def __init__(self, base:str, key:str, ) -> None:
        self.e_type = TErrorInfo.EET_INTERNAL
        self.base = base
        self.key = key
    def __str__(self) -> str:
        return f"Key \"{self.key}\" has found in base \"{self.base}\""
