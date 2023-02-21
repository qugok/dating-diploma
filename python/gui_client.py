
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

class ClientApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py

        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.readButton.clicked.connect(self.read_user)
        self.writeButton.clicked.connect(self.write_user)

    def read_user(self):
        self.status.setText("Preparing Read Request")
        key_text = self.KeyData.toPlainText()
        key = user_pb2.TUserKey()
        try:
            text_format.Parse(key_text, key)
            with grpc.insecure_channel('51.250.13.10:50051') as channel:
                stub = dating_server_pb2_grpc.DatingServerStub(channel)
                self.status.setText("Requesting Read...")
                response = stub.GetUser(dating_server_pb2.UserRequest(Key=key))
                self.UserData.setText(text_format.MessageToString(response.User))
                self.status.setText("Success Read")
        except Exception as e:
            self.status.setText("Exception: " + str(e))

    def write_user(self):
        self.status.setText("Preparing Write Request")
        user_text = self.UserDataEdit.toPlainText()
        user = user_pb2.TUser()
        try:
            text_format.Parse(user_text, user)
            with grpc.insecure_channel('51.250.13.10:50051') as channel:
                stub = dating_server_pb2_grpc.DatingServerStub(channel)
                self.status.setText("Requesting Write...")
                response:dating_server_pb2.SetUserReply = stub.SetUser(dating_server_pb2.SetUserRequest(User=user))
                if response.ErrorMessage is not None:
                    self.status.setText("Got Error:" + response.ErrorMessage)
                if response.HasField("User"):
                    self.UserDataEdit.setText(text_format.MessageToString(response.User))
        except Exception as e:
            self.status.setText("Exception: " + str(e))

def run():
    print("Starting Add ... ")
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ClientApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    print("App Started!")
    app.exec_()  # и запускаем приложение

    # with grpc.insecure_channel('51.250.13.10:50051') as channel:
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
"""
