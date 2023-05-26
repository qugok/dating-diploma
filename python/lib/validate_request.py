import generated.dating_server_pb2 as dating_server_pb2
import generated.user_pb2 as user_pb2
import logging

logger = logging.getLogger("lib")

class Validator:
    def validate(self, method_name, request):
        return getattr(self, f'validate_{method_name}')(request)

    def validate_DownloadMedia(self, request:dating_server_pb2.DownloadMediaRequest):
        error = ""
        if not request.HasField("Media"):
            error += "Media should be set"
        if not request.Media.Type or not request.Media.Path:
            error += "Media.Type and Media.Path are to be set"
        return error if error else None

    def validate_UploadMedia(self, request:dating_server_pb2.UploadMediaRequest):
        error = ""
        if not request.HasField("Media"):
            error += "Media should be set; "
        if not request.Media.LoadType == user_pb2.TLoadingMedia.ELT_FULL:
            error += "LoadType should be ELT_FULL; "
        if request.Media.PartNumber:
            error += "PartNumber should not be set; "
        if not request.Media.Type:
            error += "Media.Type should be set; "
        if request.Media.Path:
            error += "Media.Path should not be set; "
        if not request.Media.Data:
            error += "Media.Data should be set; "
            # or request.Media.LoadType == user_pb2.TLoadingMedia.ELT_BY_PART and request.Media.PartNumber
            # TODO раскомментить когда ELT_BY_PART будет поддержан
        return error if error else None

    def validate_GetUser(self, request:dating_server_pb2.GetUserRequest):
        if not request.UID:
            return "UID should be set; "
        return None

    def _good_age(self, age):
        if not age:
            return "age should be set; "
        if not 18 <= age <= 100:
            return "age should be in [18, 100]; "
        return ""

    def _validate_interests(self, interests: user_pb2.TInterests):
        if not interests.AgeFrom or not interests.AgeTo:
            return "AgeFrom and AgeTo are to be set; "
        error = ""
        error += self._good_age(interests.AgeFrom)
        error += self._good_age(interests.AgeTo)
        if interests.AgeFrom > interests.AgeTo:
            error += "AgeFrom should be less then AgeTo; "
        return error

    def _validate_user(self, user: user_pb2.TUser):
        error = ""
        if not user.UID:
            error += "UID should be set; "
        if not user.Name:
            error += "Name should be set; "
        if not user.Description:
            error += "Description should be set; "
        if not user.LastGeo:
            error += "LastGeo should be set; "
        if not user.Gender:
            error += "Gender should be set; "
        if not user.Age:
            error += "Age should be set; "
        else:
            error += self._good_age(user.Age)
        # if not user.HasField("Interests"):
        #     error += "Interests should be set; "
        # else:
        #     error += self._validate_interests(user.Interests)
        if user.HasField("Interests"):
            error += self._validate_interests(user.Interests)
        return error

    def _validate_Media(self, medias):
        for media in medias:
            if len(media.Path) > 60:
                return "media path should be shorter than 60; "
        return ""

    def validate_RegisterUser(self, request:dating_server_pb2.RegisterUserRequest):
        if not request.HasField("User"):
            return "User should be set; "
        error = ""
        error += self._validate_Media(request.User.Media)
        error += self._validate_user(request.User)
        return error if error else None

    def validate_UpdateUser(self, request:dating_server_pb2.UpdateUserRequest):
        if not request.HasField("UserDelta"):
            return "UserDelta should be set; "
        error = ""
        error += self._validate_Media(request.UserDelta.Media)
        if not request.UserDelta.UID:
            error += "UID should be set; "
        if request.UserDelta.HasField("Interests"):
            error += self._validate_interests(request.UserDelta.Interests)
        return error if error else None


    def validate_SearchUsers(self, request:dating_server_pb2.SearchUsersRequest):
        error = ""
        if not request.UID:
            error += "UID should be set; "
        if not request.Distance:
            error += "Distance should be set; "
        if not request.HasField("Geo"):
            error += "Geo should be set; "
        return error if error else None

    def validate_SetMessageToken(self, request:dating_server_pb2.SetMessageTokenRequest):
        error = ""
        if not request.UID:
            error += "UID should be set; "
        if not request.Token:
            error += "Token should be set; "
        return error if error else None

    def validate_GetReactions(self, request:dating_server_pb2.GetReactionsRequest):
        error = ""
        if not request.FromUID and not request.ToUID:
            error += "FromUID or ToUID should be set; "
        return error if error else None

    def validate_SetReaction(self, request:dating_server_pb2.SetReactionRequest):
        error = ""
        if not request.FromUID:
            error += "FromUID should be set; "
        if not request.ToUID:
            error += "ToUID should be set; "
        if not request.Reaction or request.Reaction == user_pb2.TReaction.ERT_UNSET:
            error += "Reaction should be set; "
        return error if error else None

    def __Message(self, message:user_pb2.TMessage):
        error = ""
        if not message.FromUID:
            error += "FromUID should be set; "
        if not message.ToUID:
            error += "ToUID should be set; "
        if message.Timestamp:
            error += "Timestamp should not be set; "
        if not message.Text:
            error += "Text should be set; "
        return error

    def validate_SendMessage(self, request:dating_server_pb2.SendMessageRequest):
        error = ""
        if len(request.Messages) == 0:
            error += "Messages should not be empty; "
        from_uids = set()
        to_uids = set()
        for m in request.Messages:
            from_uids.add(m.FromUID)
            to_uids.add(m.ToUID)
            error += self.__Message(m)

        if len(from_uids) > 1:
            error += f"all messages in request should be from one UID, got UIDs: {from_uids};"
        if len(to_uids) > 1:
            error += f"all messages in request should be to one UID, got UIDs: {to_uids};"
        return error if error else None

    def validate_GetLastMessages(self, request:dating_server_pb2.GetLastMessagesRequest):
        error = ""
        if not request.FromUID:
            error += "FromUID should be set; "
        if not request.ToUID:
            error += "ToUID should be set; "
        return error if error else None

    def validate_GetChats(self, request:dating_server_pb2.GetChatsRequest):
        error = ""
        if not request.UID:
            error += "UID should be set; "
        return error if error else None
