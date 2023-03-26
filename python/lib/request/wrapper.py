
import generated.misc_pb2 as misc_pb2

def SetOkReplyStatus(reply):
    reply.Status = misc_pb2.EReplyStatus.ERS_OK
    return reply

def SetErrorReply(reply, errorMessage:str, error_type:misc_pb2.TErrorInfo.EErrorType=misc_pb2.TErrorInfo.EET_UNKNOWN):
    reply.Status = misc_pb2.EReplyStatus.ERS_ERROR
    reply.Error.Message = errorMessage
    reply.Error.Type = error_type
    return reply
