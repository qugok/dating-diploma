# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(831, 540)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.status = QtWidgets.QLabel(self.centralwidget)
        self.status.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.status.setMouseTracking(True)
        self.status.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setOpenExternalLinks(False)
        self.status.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.UserKeyFrom = QtWidgets.QLineEdit(self.centralwidget)
        self.UserKeyFrom.setObjectName("UserKeyFrom")
        self.verticalLayout_6.addWidget(self.UserKeyFrom)
        self.UserKeyTo = QtWidgets.QLineEdit(self.centralwidget)
        self.UserKeyTo.setObjectName("UserKeyTo")
        self.verticalLayout_6.addWidget(self.UserKeyTo)
        self.AuthToken = QtWidgets.QLineEdit(self.centralwidget)
        self.AuthToken.setObjectName("AuthToken")
        self.verticalLayout_6.addWidget(self.AuthToken)
        self.RequestData = QtWidgets.QTextEdit(self.centralwidget)
        self.RequestData.setObjectName("RequestData")
        self.verticalLayout_6.addWidget(self.RequestData)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.GetRelationsRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.GetRelationsRadioButton.setObjectName("GetRelationsRadioButton")
        self.gridLayout.addWidget(self.GetRelationsRadioButton, 1, 0, 1, 2)
        self.GetMessagesRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.GetMessagesRadioButton.setObjectName("GetMessagesRadioButton")
        self.gridLayout.addWidget(self.GetMessagesRadioButton, 2, 0, 1, 2)
        self.SendRelationRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.SendRelationRadioButton.setObjectName("SendRelationRadioButton")
        self.gridLayout.addWidget(self.SendRelationRadioButton, 1, 2, 1, 2)
        self.SendMessageRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.SendMessageRadioButton.setObjectName("SendMessageRadioButton")
        self.gridLayout.addWidget(self.SendMessageRadioButton, 2, 2, 1, 2)
        self.ReadUserRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.ReadUserRadioButton.setObjectName("ReadUserRadioButton")
        self.gridLayout.addWidget(self.ReadUserRadioButton, 3, 0, 1, 2)
        self.UpdateUserRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.UpdateUserRadioButton.setObjectName("UpdateUserRadioButton")
        self.gridLayout.addWidget(self.UpdateUserRadioButton, 3, 2, 1, 2)
        self.RegisterUserRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.RegisterUserRadioButton.setObjectName("RegisterUserRadioButton")
        self.gridLayout.addWidget(self.RegisterUserRadioButton, 4, 2, 1, 2)
        self.SearchUsersRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.SearchUsersRadioButton.setObjectName("SearchUsersRadioButton")
        self.gridLayout.addWidget(self.SearchUsersRadioButton, 4, 0, 1, 2)
        self.DownloadMediaRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.DownloadMediaRadioButton.setObjectName("DownloadMediaRadioButton")
        self.gridLayout.addWidget(self.DownloadMediaRadioButton, 0, 0, 1, 2)
        self.UploadMediaRadioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.UploadMediaRadioButton.setObjectName("UploadMediaRadioButton")
        self.gridLayout.addWidget(self.UploadMediaRadioButton, 0, 2, 1, 2)
        self.verticalLayout_6.addLayout(self.gridLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_6)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.ReplyText = QtWidgets.QTextBrowser(self.centralwidget)
        self.ReplyText.setObjectName("ReplyText")
        self.verticalLayout_5.addWidget(self.ReplyText)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.MakeRequest = QtWidgets.QPushButton(self.centralwidget)
        self.MakeRequest.setObjectName("MakeRequest")
        self.horizontalLayout_4.addWidget(self.MakeRequest)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.status.setText(_translate("MainWindow", "Info"))
        self.UserKeyFrom.setPlaceholderText(_translate("MainWindow", "key from "))
        self.UserKeyTo.setPlaceholderText(_translate("MainWindow", "key to"))
        self.AuthToken.setPlaceholderText(_translate("MainWindow", "auth token"))
        self.RequestData.setPlaceholderText(_translate("MainWindow", "data"))
        self.GetRelationsRadioButton.setText(_translate("MainWindow", "GetRelations"))
        self.GetMessagesRadioButton.setText(_translate("MainWindow", "GetMessages"))
        self.SendRelationRadioButton.setText(_translate("MainWindow", "SendRelation"))
        self.SendMessageRadioButton.setText(_translate("MainWindow", "SendMessage"))
        self.ReadUserRadioButton.setText(_translate("MainWindow", "ReadUser"))
        self.UpdateUserRadioButton.setText(_translate("MainWindow", "UpdateUser"))
        self.RegisterUserRadioButton.setText(_translate("MainWindow", "RegisterUser"))
        self.SearchUsersRadioButton.setText(_translate("MainWindow", "SearchUsers"))
        self.DownloadMediaRadioButton.setText(_translate("MainWindow", "DownloadMedia"))
        self.UploadMediaRadioButton.setText(_translate("MainWindow", "UploadMedia"))
        self.ReplyText.setPlaceholderText(_translate("MainWindow", "Reply"))
        self.MakeRequest.setText(_translate("MainWindow", "Make Request"))
