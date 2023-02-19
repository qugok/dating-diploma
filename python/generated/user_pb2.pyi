#!/home/alex/anaconda3/bin/python

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TPhoto(_message.Message):
    __slots__ = ["Data", "Type"]
    class EPhotoType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    DATA_FIELD_NUMBER: _ClassVar[int]
    Data: bytes
    EPT_JPG: TPhoto.EPhotoType
    EPT_UNKNOWN: TPhoto.EPhotoType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    Type: TPhoto.EPhotoType
    def __init__(self, Type: _Optional[_Union[TPhoto.EPhotoType, str]] = ..., Data: _Optional[bytes] = ...) -> None: ...

class TUser(_message.Message):
    __slots__ = ["Descripton", "Key", "Name", "Photos"]
    DESCRIPTON_FIELD_NUMBER: _ClassVar[int]
    Descripton: str
    KEY_FIELD_NUMBER: _ClassVar[int]
    Key: TUserKey
    NAME_FIELD_NUMBER: _ClassVar[int]
    Name: str
    PHOTOS_FIELD_NUMBER: _ClassVar[int]
    Photos: _containers.RepeatedCompositeFieldContainer[TPhoto]
    def __init__(self, Key: _Optional[_Union[TUserKey, _Mapping]] = ..., Name: _Optional[str] = ..., Descripton: _Optional[str] = ..., Photos: _Optional[_Iterable[_Union[TPhoto, _Mapping]]] = ...) -> None: ...

class TUserKey(_message.Message):
    __slots__ = ["Hash"]
    HASH_FIELD_NUMBER: _ClassVar[int]
    Hash: int
    def __init__(self, Hash: _Optional[int] = ...) -> None: ...
