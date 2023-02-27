
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

def make_simple_request(request_func):
    def wrapper(self):
        self.status.setText(f"Preparing {request_func.__name__} Request")
        try:
            with grpc.insecure_channel(self.server_address) as channel:
                stub = dating_server_pb2_grpc.DatingServerStub(channel)

                response = request_func(self, stub)

            self.ReplyText.setText(text_format.MessageToString(response, True))
            if not response.HasField("Error"):
                self.status.setText(f"Success {request_func.__name__}")
            else :
                self.status.setText(f"Error : {response.Error.ErrorMessage}")
        except Exception as e:
            self.status.setText("Exception: " + str(e))

    return wrapper

class ClientApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py

        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.server_address = "51.250.13.10:50051"
        # self.readButton.clicked.connect(self.read_user)
        # self.writeButton.clicked.connect(self.write_user)
        self.SearchUsers.clicked.connect(self.search)
        self.MakeRequest.clicked.connect(self.request)
        self.status.setText("приветики")

    def request(self):
        if self.ReadUserRadioButton.isChecked():
            self.read_user()
        elif self.WriteUserRadioButton.isChecked():
            self.write_user()
        elif self.GetRelationsRadioButton.isChecked():
            self.get_relations()
        elif self.SendRelationRadioButton.isChecked():
            self.send_relations()
        elif self.GetMessagesRadioButton.isChecked():
            self.get_messages()
        elif self.SendMessageRadioButton.isChecked():
            self.send_message()

    def __fill_request_keys(self, request):
        if self.UserKeyTo.text:
            text_format.Parse(self.UserKeyTo.text(), request.To)
        if self.UserKeyFrom.text:
            text_format.Parse(self.UserKeyFrom.text(), request.From)

    @make_simple_request
    def read_user(self, stub):
        request = dating_server_pb2.GetUserRequest()
        text_format.Parse(self.UserKeyFrom.text(), request.Key)

        return stub.GetUser(request)

    @make_simple_request
    def write_user(self, stub):
        request = dating_server_pb2.SetUserRequest()
        text_format.Parse(self.RequestData.toPlainText(), request.User)

        return stub.SetUser(request)

    @make_simple_request
    def get_relations(self, stub):
        request = dating_server_pb2.GetReactionsRequest()
        self.__fill_request_keys(request)

        return stub.GetReactions(request)

    @make_simple_request
    def send_relations(self, stub):
        request = dating_server_pb2.SetReactionRequest()
        self.__fill_request_keys(request)
        text_format.Parse(self.RequestData.toPlainText(), request.Reaction)

        return stub.SetReaction(request)

    @make_simple_request
    def get_messages(self, stub):
        request = dating_server_pb2.GetLastMessagesRequest()
        self.__fill_request_keys(request)

        return stub.GetLastMessages(request)

    @make_simple_request
    def send_message(self, stub):
        request = dating_server_pb2.SendMessageRequest()
        message = request.Messages.add()
        text_format.Parse(self.UserKeyTo.text(), message.ToKey)
        text_format.Parse(self.UserKeyFrom.text(), message.FromKey)
        message.Text = self.RequestData.toPlainText()

        return stub.SendMessage(request)

    def search(self):
        if self.NearestUser.isChecked():
            self.__find_nearest()
        else:
            self.__search_users()

    def __search_users(self):
        self.status.setText("Preparing Search Request")
        geo_text = self.GeoInfo.toPlainText()
        geo = user_pb2.TGeo()
        try:
            text_format.Parse(geo_text, geo)
            with grpc.insecure_channel(self.server_address) as channel:
                stub = dating_server_pb2_grpc.DatingServerStub(channel)
                self.status.setText("Requesting Search...")
                response:dating_server_pb2.NeighboursReply = stub.SearchAllNeighbours(dating_server_pb2.NeighboursRequest(Geo=geo))
                self.UsersKeys.setText(text_format.MessageToString(response, True))
        except Exception as e:
            self.status.setText("Exception: " + str(e))

    def __find_nearest(self):
        self.status.setText("Preparing Find Request")
        geo_text = self.GeoInfo.toPlainText()
        geo = user_pb2.TGeo()
        try:
            text_format.Parse(geo_text, geo)
            with grpc.insecure_channel(self.server_address) as channel:
                stub = dating_server_pb2_grpc.DatingServerStub(channel)
                self.status.setText("Requesting Find...")
                response:dating_server_pb2.NearestReply = stub.FindNearest(dating_server_pb2.NearestRequest(Geo=geo))
                self.UsersKeys.setText(text_format.MessageToString(response, True))
        except Exception as e:
            self.status.setText("Exception: " + str(e))

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
Key {
  Hash: 4567890987
}
Name: "Alex"
Descripton: "ай, выхади за меня дарагая, лучшый парень ever!"
LastGeo {
  Latitude: 50.000000
  Longitude: 1.000000
}



Key {
  Hash: 4563453387
}
Name: "Ally"
Descripton: "Привет"
LastGeo {
  Latitude: 50.962057
  Longitude: 1.954764
}


TUserKey FromKey = 1;
  TUserKey ToKey = 2;
  uint64 Timestamp = 4;

  // Контент
  string Text = 10;

"""
