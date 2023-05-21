import generated.dating_server_pb2 as dating_server_pb2
import generated.user_pb2 as user_pb2
import logging

logger = logging.getLogger("lib")

class Validator:
    def validate(self, method_name, request):
        return getattr(self, f'validate_{method_name}')(request)

    def validate_DownloadMedia(self, request:dating_server_pb2.DownloadMediaRequest):
        return request.HasField("Media") and request.Media.Type and request.Media.Path

    def validate_UploadMedia(self, request:dating_server_pb2.UploadMediaRequest):
        if not request.HasField("Media"):
            return False
        valid_load_type = request.Media.LoadType == user_pb2.TLoadingMedia.ELT_FULL and not request.Media.PartNumber
            # or request.Media.LoadType == user_pb2.TLoadingMedia.ELT_BY_PART and request.Media.PartNumber
            # TODO раскомментить когда ELT_BY_PART будет поддержан

        return request.HasField("Media") and valid_load_type and\
                request.Media.Type and \
                not request.Media.Path and \
                request.Media.Data

    def validate_GetUser(self, request:dating_server_pb2.GetUserRequest):
        return not not request.UID

    def _good_age(self, age):
            return age and 18 <= age <= 100

    def _validate_interests(self, interests: user_pb2.TInterests):
        if self._good_age(interests.AgeFrom) and self._good_age(interests.AgeTo) and interests.AgeFrom > interests.AgeTo:
            return False
        return True

    def _validate_user(self, user: user_pb2.TUser):
        base_fields = user.UID and \
                    user.Name and \
                    user.Description and \
                    user.LastGeo and \
                    user.SearchDistanceKm and \
                    user.Gender and \
                    self._good_age(user.Age)
        interests = self._validate_interests(user.Interests) if user.HasField("Interests") else True
        interests = True
        return base_fields and interests


    def validate_RegisterUser(self, request:dating_server_pb2.RegisterUserRequest):
        if not request.HasField("User"):
            return False
        for media in request.User.Media:
            if len(media.Path) > 60:
                return False
        return self._validate_user(request.User)

    def validate_UpdateUser(self, request:dating_server_pb2.UpdateUserRequest):
        for media in request.UserDelta.Media:
            if len(media.Path) > 60:
                return False
        return request.HasField("UserDelta") and request.UserDelta.UID \
            and (self._validate_interests(request.UserDelta.Interests) if request.UserDelta.HasField("Interests") else True)

    def validate_SearchUsers(self, request:dating_server_pb2.SearchUsersRequest):
        return request.UID and request.HasField("Geo") and request.Distance

    def validate_SetMessageToken(self, request:dating_server_pb2.SetMessageTokenRequest):
        return request.UID and request.Token

    def validate_GetReactions(self, request:dating_server_pb2.GetReactionsRequest):
        return request.FromUID or request.ToUID

    def validate_SetReaction(self, request:dating_server_pb2.SetReactionRequest):
        return request.FromUID and request.ToUID and request.Reaction and request.Reaction != user_pb2.TReaction.ERT_UNSET

    def __Message(self, message:user_pb2.TMessage):
        return message.FromUID and message.ToUID \
            and not message.Timestamp and message.Text

    def validate_SendMessage(self, request:dating_server_pb2.SendMessageRequest):
        if len(request.Messages) == 0:
            return False
        for m in request.Messages:
            if not self.__Message(m):
                return False

        return True

    def validate_GetLastMessages(self, request:dating_server_pb2.GetLastMessagesRequest):
        return request.FromUID and request.ToUID

    def validate_GetChats(self, request:dating_server_pb2.GetChatsRequest):
        return not not request.UID
