
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets

import logging
sys.path.append('./generated')

import grpc
import generated.user_pb2 as user_pb2
import generated.dating_server_pb2 as dating_server_pb2
import generated.dating_server_pb2_grpc as dating_server_pb2_grpc
import user_utils

from google.protobuf import text_format

import design

def make_simple_request(request_class):
    def real_decorator(request_func):
        def wrapper(self):
            self.status.setText(f"Preparing {request_func.__name__} Request")
            try:
                token = self.AuthToken.text()
                with grpc.insecure_channel(self.server_address) as channel:
                    stub = dating_server_pb2_grpc.DatingServerStub(channel)
                    request = request_class()
                    if token:
                        request.Auth.Token = token
                    response = request_func(self, request, stub)

                self.ReplyText.setText(text_format.MessageToString(response, True))
                if not response.HasField("Error"):
                    self.status.setText(f"Success {request_func.__name__}")
                else :
                    self.status.setText(f"Error : {response.Error.Message}")
            except Exception as e:
                self.status.setText("Exception: " + str(e))
        return wrapper
    return real_decorator

class ClientApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py

        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        # self.server_address = "51.250.13.10:50051"
        self.server_address = "51.250.13.10:55555"
        self.MakeRequest.clicked.connect(self.request)
        self.status.setText("приветики")

    def request(self):
        if self.ReadUserRadioButton.isChecked():
            self.read_user()
        elif self.RegisterUserRadioButton.isChecked():
            self.register_user()
        elif self.UpdateUserRadioButton.isChecked():
            self.update_user()

        elif self.GetRelationsRadioButton.isChecked():
            self.get_relations()
        elif self.SendRelationRadioButton.isChecked():
            self.send_relations()

        elif self.GetMessagesRadioButton.isChecked():
            self.get_messages()
        elif self.SendMessageRadioButton.isChecked():
            self.send_message()

        elif self.SearchUsersRadioButton.isChecked():
            self.search_users()

    def __fill_request_keys(self, request):
        request.ToUID = self.UserKeyTo.text()
        request.FromUID = self.UserKeyFrom.text()

    @make_simple_request(dating_server_pb2.GetUserRequest)
    def read_user(self, request, stub):
        request.UID = self.UserKeyFrom.text()

        return stub.GetUser(request)

    @make_simple_request(dating_server_pb2.RegisterUserRequest)
    def register_user(self, request, stub):
        text_format.Parse(self.RequestData.toPlainText(), request.User)

        return stub.RegisterUser(request)

    @make_simple_request(dating_server_pb2.UpdateUserRequest)
    def update_user(self, request, stub):
        text_format.Parse(self.RequestData.toPlainText(), request.User)

        return stub.UpdateUser(request)

    @make_simple_request(dating_server_pb2.GetReactionsRequest)
    def get_relations(self, request, stub):
        self.__fill_request_keys(request)

        return stub.GetReactions(request)

    @make_simple_request(dating_server_pb2.SetReactionRequest)
    def send_relations(self, request, stub):
        self.__fill_request_keys(request)
        request.Reaction = self.RequestData.toPlainText()

        return stub.SetReaction(request)

    @make_simple_request(dating_server_pb2.GetLastMessagesRequest)
    def get_messages(self, request, stub):
        self.__fill_request_keys(request)

        return stub.GetLastMessages(request)

    @make_simple_request(dating_server_pb2.SendMessageRequest)
    def send_message(self, request, stub):
        message = request.Messages.add()
        message.ToUID = self.UserKeyTo.text()
        message.FromUID = self.UserKeyFrom.text()
        message.Text = self.RequestData.toPlainText()

        return stub.SendMessage(request)

    @make_simple_request(dating_server_pb2.SearchUsersRequest)
    def search_users(self, request, stub):
        request.UID = self.UserKeyFrom.text()

        return stub.SearchUsers(request)

def run():
    print("Starting Add ... ")
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ClientApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    print("App Started!")
    app.exec_()  # и запускаем приложение

    # with grpc.insecure_channel(self.server_address) as channel:
    #     stub = dating_server_pb2_grpc.DatingServerStub(channel)
    #     key = user_pb2.TUserKey(Hash=4567890987)
    #     response = stub.GetUser(dating_server_pb2.UserRequest(Key=key))
    # print("Greeter client received: \n" + user_utils.UserToString(response.User))


if __name__ == '__main__':
    logging.basicConfig()
    run()


"""

UID: "sgbgbfstgbsrtgbsr"
Name: "Alex"
Descripton: "ай, выхади за меня дарагая, лучшый парень ever!"
LastGeo {
  Latitude: 50.000000
  Longitude: 1.000000
}

UID: "asdasdasdadasd"
Name: "Ally"
Descripton: "Привет"
LastGeo {
  Latitude: 50.962057
  Longitude: 1.954764
}



UID: "GQMCVmgBP7YNFNU9zpagdSV4CCo2"
Name: "Authorized User"
Descripton: "Привет, я пользователь, у которого есть настоящий токен аутентификации"
LastGeo {
  Latitude: 50.000000
  Longitude: 1.000000
}
SearchDistanceKm: 25

Auth {
    Token: "eyJhbGciOiJSUzI1NiIsImtpZCI6IjFlOTczZWUwZTE2ZjdlZWY0ZjkyMWQ1MGRjNjFkNzBiMmVmZWZjMTkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vc29uZGVyLWRhdGluZy1hcHAiLCJhdWQiOiJzb25kZXItZGF0aW5nLWFwcCIsImF1dGhfdGltZSI6MTY3NzQzMjMwMiwidXNlcl9pZCI6IkdRTUNWbWdCUDdZTkZOVTl6cGFnZFNWNENDbzIiLCJzdWIiOiJHUU1DVm1nQlA3WU5GTlU5enBhZ2RTVjRDQ28yIiwiaWF0IjoxNjc5MjM0Mzg0LCJleHAiOjE2NzkyMzc5ODQsInBob25lX251bWJlciI6Iis3OTE2MDg3MjEzMSIsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsicGhvbmUiOlsiKzc5MTYwODcyMTMxIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGhvbmUifX0.hupKx9G0QqNaT7tCw5CpALVvKkO6vI1T4WP5AlaHWIejzN1fihXQpyhtdZB1iRTLHB2c1aKxpdpY_TIS5p51yp5rYzYNGL4h-nzOcAHPkbKnaS19jUnJTyL4dks9r1jGNVi5jSzIK6XMHLtbh-sm3bbbsk2ukkKLMFkMSg_lT08bwfAKpAFJiOY998CvkmR6x4P25xHg4X6KmcFFV11e7GqVDoDydDatJvBLgxxpkTxL1Iknhf4Qwm8YzyHvYBr4hzQgcu9V2xJz8j5Tb7dZLFehPEJbflgySYNtQHbwhP0jiNS_RJMJBssZJ61Pr1LoAtcxpExx4dSGHCNS5Ex0PA"
}

eyJhbGciOiJSUzI1NiIsImtpZCI6IjFlOTczZWUwZTE2ZjdlZWY0ZjkyMWQ1MGRjNjFkNzBiMmVmZWZjMTkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vc29uZGVyLWRhdGluZy1hcHAiLCJhdWQiOiJzb25kZXItZGF0aW5nLWFwcCIsImF1dGhfdGltZSI6MTY3NzQzMjMwMiwidXNlcl9pZCI6IkdRTUNWbWdCUDdZTkZOVTl6cGFnZFNWNENDbzIiLCJzdWIiOiJHUU1DVm1nQlA3WU5GTlU5enBhZ2RTVjRDQ28yIiwiaWF0IjoxNjc5MjM0Mzg0LCJleHAiOjE2NzkyMzc5ODQsInBob25lX251bWJlciI6Iis3OTE2MDg3MjEzMSIsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsicGhvbmUiOlsiKzc5MTYwODcyMTMxIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGhvbmUifX0.hupKx9G0QqNaT7tCw5CpALVvKkO6vI1T4WP5AlaHWIejzN1fihXQpyhtdZB1iRTLHB2c1aKxpdpY_TIS5p51yp5rYzYNGL4h-nzOcAHPkbKnaS19jUnJTyL4dks9r1jGNVi5jSzIK6XMHLtbh-sm3bbbsk2ukkKLMFkMSg_lT08bwfAKpAFJiOY998CvkmR6x4P25xHg4X6KmcFFV11e7GqVDoDydDatJvBLgxxpkTxL1Iknhf4Qwm8YzyHvYBr4hzQgcu9V2xJz8j5Tb7dZLFehPEJbflgySYNtQHbwhP0jiNS_RJMJBssZJ61Pr1LoAtcxpExx4dSGHCNS5Ex0PA

ERT_UNSET
ERT_LIKE
ERT_DISLIKE

"""
