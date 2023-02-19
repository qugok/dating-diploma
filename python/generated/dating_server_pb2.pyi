import user_pb2 as _user_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetUserReply(_message.Message):
    __slots__ = ["ErrorMessage", "User"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    ErrorMessage: str
    USER_FIELD_NUMBER: _ClassVar[int]
    User: _user_pb2.TUser
    def __init__(self, User: _Optional[_Union[_user_pb2.TUser, _Mapping]] = ..., ErrorMessage: _Optional[str] = ...) -> None: ...

class SetUserRequest(_message.Message):
    __slots__ = ["User"]
    USER_FIELD_NUMBER: _ClassVar[int]
    User: _user_pb2.TUser
    def __init__(self, User: _Optional[_Union[_user_pb2.TUser, _Mapping]] = ...) -> None: ...

class UserReply(_message.Message):
    __slots__ = ["User"]
    USER_FIELD_NUMBER: _ClassVar[int]
    User: _user_pb2.TUser
    def __init__(self, User: _Optional[_Union[_user_pb2.TUser, _Mapping]] = ...) -> None: ...

class UserRequest(_message.Message):
    __slots__ = ["Key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    Key: _user_pb2.TUserKey
    def __init__(self, Key: _Optional[_Union[_user_pb2.TUserKey, _Mapping]] = ...) -> None: ...
