import logging

from lib.request.wrapper import SetErrorReply, SetOkReplyStatus
from generated.misc_pb2 import TErrorInfo
from lib.exceptions import DatingServerException, WrongRequest
import traceback
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from lib.tools.proto_utils import FullMessageToDict

logger = logging.getLogger("decorators")
logger.setLevel(logging.DEBUG)

def process_simple_request(reply_class):


    def real_decorator(request_func=None):
        def wrapper(self, request, context):
            logger.debug(f"preparing {str(request_func.__name__)}")
            try:
                logger.debug(f"authentication user auth {FullMessageToDict(request.Auth)}")
                user_auth_info = self.auth.authenticate_user(request.Auth)
                logger.debug(f"authentication got user_auth_info: {user_auth_info}")
                if user_auth_info is None:
                    logger.debug(f"ErrorReply: authentication user_auth_info: {user_auth_info}")
                    return SetErrorReply(
                        reply_class(),
                        f"authentication error for user auth {FullMessageToDict(request.Auth)}",
                        TErrorInfo.EET_AUTHORIZATION
                    )
                if not self.auth.authorize_user(user_auth_info, request_func.__name__, request):
                    logger.debug(f"ErrorReply: authorization failed: {user_auth_info} {request_func.__name__} {FullMessageToDict(request)}")
                    return SetErrorReply(
                        reply_class(),
                        f"authorization error for user {user_auth_info.uid}",
                        TErrorInfo.EET_AUTHORIZATION
                    )

                logger.debug(f"authorixed as {user_auth_info.uid}")
            except Exception as e:
                logger.debug(f"got exception 1 {str(e) + str(traceback.format_exc())}")
                return SetErrorReply(
                    reply_class(),
                    str(e) + str(traceback.format_exc()),
                    TErrorInfo.EET_AUTHENTIFICATION
                )

            try:
                logger.debug(f"Processiong {request_func.__name__} request: {FullMessageToDict(request, True)}")
                error = self.validator.validate(request_func.__name__, request)
                if error is not None:
                    raise WrongRequest(f"validation failed. Type: {request_func.__name__} request: {FullMessageToDict(request, True)}; error message: {error}")
                logger.debug(f"Valid request: {request_func.__name__} request: {FullMessageToDict(request, True)}")
                kws = request_func(self, request, context, user_auth_info)
                logger.debug(f"Processed {request_func.__name__} request, result: {FullMessageToDict(kws)}")
                return SetOkReplyStatus(
                    reply_class(**kws)
                )
            except DatingServerException as e:
                logger.debug(f"got DatingServerException {str(e) + str(traceback.format_exc())}")
                return SetErrorReply(
                    reply_class(),
                    str(e),
                    e.e_type
                )
            except Exception as e:
                logger.error(f"{request_func.__name__}: got exception :: {e} {traceback.format_exc()}")
                return SetErrorReply(
                    reply_class(),
                    str(e) + str(traceback.format_exc()),
                    TErrorInfo.EET_INTERNAL
                )
        return wrapper
    return real_decorator
