# import sys, os
# sys.path.append('./generated')


import generated.misc_pb2 as misc_pb2
import generated.user_pb2 as user_pb2
import grpc
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc

def SetOkReplyStatus(reply):
    reply.Status = misc_pb2.EReplyStatus.ERS_OK
    return reply

def SetErrorReply(reply, errorMessage:str):
    reply.Status = misc_pb2.EReplyStatus.ERS_ERROR
    reply.Error.ErrorMessage = errorMessage
    return reply

def UserKeyToKeyString(key: user_pb2.TUserKey):
    return str(key.Hash)

def UserKeyToKeyInteger(key: user_pb2.TUserKey):
    return key.Hash

def UserKeyFromKeyString(key: str):
    return user_pb2.TUserKey(int(key))
