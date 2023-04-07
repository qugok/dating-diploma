import logging

from lib.request.wrapper import SetErrorReply, SetOkReplyStatus
from generated.misc_pb2 import TErrorInfo
from lib.exceptions import DatingServerException, WrongRequest
import traceback
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger(__name__)

def process_simple_request(reply_class):
    def MessageToDictWithoutAuth(message):
        js_dict:dict= MessageToDict(message)
        if "Auth" in js_dict:
            js_dict.pop("Auth")
        return js_dict

    def real_decorator(request_func=None):
        def wrapper(self, request, context):
            logger.debug(f"preparing {str(request_func.__name__)}")
            logging.info(f"preparing {str(request_func.__name__)}")
            try:
                user_auth_info = self.auth.authenticate_user(request.Auth)
                if not user_auth_info:
                    return SetErrorReply(
                        reply_class(),
                        f"authentication error for user auth {MessageToDict(request.Auth)}",
                        TErrorInfo.EET_AUTHORIZATION
                    )
                if not self.auth.authorize_user(user_auth_info, request_func.__name__, request):
                    return SetErrorReply(
                        reply_class(),
                        f"authorization error for user {user_auth_info.uid}",
                        TErrorInfo.EET_AUTHORIZATION
                    )

                logger.debug(f"authorixed as {user_auth_info.uid}")
            except Exception as e:
                return SetErrorReply(
                    reply_class(),
                    str(e) + str(traceback.format_exc()),
                    TErrorInfo.EET_AUTHENTIFICATION
                )

            try:
                logger.debug(f"Processiong {request_func.__name__} request: {MessageToDictWithoutAuth(request)}")
                if not self.validator.validate(request_func.__name__, request):
                    raise WrongRequest(f"validation failed. Type: {request_func.__name__} request: {MessageToDictWithoutAuth(request)}")
                kws = request_func(self, request, context, user_auth_info)
                return SetOkReplyStatus(
                    reply_class(**kws)
                )
            except DatingServerException as e:
                return SetErrorReply(
                    reply_class(),
                    str(e),
                    e.e_type
                )
            except Exception as e:
                logger.error(f"{request_func.__name__}: got exception :: {e}")
                return SetErrorReply(
                    reply_class(),
                    str(e) + str(traceback.format_exc()),
                    TErrorInfo.EET_INTERNAL
                )
        return wrapper
    return real_decorator
