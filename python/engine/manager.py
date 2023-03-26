import generated.user_pb2 as user_pb2
from lib.couchbase.client import CouchbaseClient


class Manager:
    # TODO добавить валидацию, где необходимо
    def __init__(self, config_path):
        # TODO добавить отдельный конфиг для менеджера
        self.couchbase_client = CouchbaseClient(config_path)
        pass

    def register_user(self, user: user_pb2.TUser):
        self.couchbase_client.insert_user(user)

        if user.HasField("LastGeo"):
            self.couchbase_client.upsert_to_geo_index(user.LastGeo)

    def update_user(self, user_delta: user_pb2.TUser):
        self.couchbase_client.update_user(user_delta)

        if user_delta.HasField("LastGeo"):
            self.couchbase_client.upsert_to_geo_index(user_delta.LastGeo)

    def get_user(self, UID: str):
        return self.couchbase_client.get_user(UID)

    def get_users_to_show(self, UID:str, distance:int=None, limit:int=None):
        # TODO добавить логики поиска подходящего человека
        user = self.couchbase_client.get_user(UID)
        distance = distance or user.SearchDistanceKm or 10
        limit = limit or 10

        uids = self.couchbase_client.search_near(user.LastGeo, f"{distance}km", limit)
        users = [self.couchbase_client.get_user(uid) for uid in uids]

        return users

    def get_reactions_from(self, UID:str):
        reactions = self.couchbase_client.get_reactions_with(UID)
        return [react for react in reactions if react.FromUID == UID]

    def get_reactions_to(self, UID:str):
        reactions = self.couchbase_client.get_reactions_with(UID)
        return [react for react in reactions if react.ToUID == UID]

    def insert_reaction(
        self,
        FromUID: str,
        ToUID: str,
        ReactionType: user_pb2.TReaction.EReactionType
    ):
        """
        добавляет реакцию, только если её не было раньше, иначе выбрасывает исключение
        TODO поставить ттл на реакции - пара месяцев
        """
        reaction = user_pb2.TReaction(FromUID=FromUID, ToUID=ToUID, ReactionType=ReactionType)

        self.couchbase_client.upsert_reaction(reaction)


    def send_messages(
        self,
        messages # repeated user_pb2.TMessage,
    ):

        self.couchbase_client.store_messages(messages)
        # TODO отправка сообщений через pusher to client

    def read_messages(
        self,
        FromUID: str,
        ToUID: str,
    ):
        messages = self.couchbase_client.read_messages_with(FromUID)
        return [message for message in messages if message.FromUID == FromUID and message.ToUID == ToUID]
