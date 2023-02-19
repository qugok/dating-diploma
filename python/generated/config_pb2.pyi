from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TPrivateData(_message.Message):
    __slots__ = ["Password", "Username"]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    Password: str
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    Username: str
    def __init__(self, Username: _Optional[str] = ..., Password: _Optional[str] = ...) -> None: ...
