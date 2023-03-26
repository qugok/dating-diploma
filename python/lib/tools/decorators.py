from lib.request.wrapper import SetErrorReply, SetOkReplyStatus
from generated.misc_pb2 import TErrorInfo
import traceback
import logging

logger = logging.getLogger("__name__")

def process_simple_request(reply_class):
    def real_decorator(request_func=None):
        def wrapper(self, request, context):
            # TODO заменить print на нормальное логгирование РАЗОБРАТЬСЯ С РАБОТОЙ ЛОГГЕРА
            print(logger, flush=True)
            logger.debug("preparing", request_func.__name__)
            logging.info("preparing", request_func.__name__)
            try :
                user_auth_info = self.auth.get_user_auth_info(request.Auth)
                if not self.auth.authorize_user(user_auth_info, request_func.__name__, request):
                    return SetErrorReply(
                        reply_class(),
                        f"authorization error for user {user_auth_info.uid}",
                        TErrorInfo.EET_AUTHORIZATION
                    )

                logger.debug("authorixed as ", user_auth_info.uid)
            except Exception as e:
                return SetErrorReply(
                    reply_class(),
                    str(e) + str(traceback.format_exc()),
                    TErrorInfo.EET_AUTHENTIFICATION
                )

            try :
                logger.debug("processing", request_func.__name__)
                kws = request_func(self, request, context, user_auth_info)
                return SetOkReplyStatus(
                    reply_class(**kws)
                )
            except Exception as e:
                logger.error(f"{request_func.__name__}: got exception ::", e)
                return SetErrorReply(
                    reply_class(),
                    str(e) + str(traceback.format_exc()),
                    TErrorInfo.EET_INTERNAL
                )
        return wrapper
    return real_decorator
