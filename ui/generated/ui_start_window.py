# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_start_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_StartWindow(object):
    def setupUi(self, StartWindow):
        if not StartWindow.objectName():
            StartWindow.setObjectName(u"StartWindow")
        StartWindow.resize(677, 249)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(StartWindow.sizePolicy().hasHeightForWidth())
        StartWindow.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u"favicon.ico", QSize(), QIcon.Normal, QIcon.Off)
        StartWindow.setWindowIcon(icon)
        self.frame = QFrame(StartWindow)
        self.frame.setObjectName(u"frame")
        self.frame.setEnabled(True)
        self.frame.setGeometry(QRect(270, 40, 371, 191))
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Raised)
        self.label_choose_project_directory = QLabel(self.frame)
        self.label_choose_project_directory.setObjectName(u"label_choose_project_directory")
        self.label_choose_project_directory.setGeometry(QRect(20, 4, 191, 41))
        self.button_create_project = QPushButton(self.frame)
        self.button_create_project.setObjectName(u"button_create_project")
        self.button_create_project.setEnabled(False)
        self.button_create_project.setGeometry(QRect(140, 150, 111, 31))
        self.button_create_project.setAutoFillBackground(False)
        self.button_choose_project_directory = QPushButton(self.frame)
        self.button_choose_project_directory.setObjectName(u"button_choose_project_directory")
        self.button_choose_project_directory.setGeometry(QRect(240, 10, 111, 31))
        self.button_choose_project_directory.setAutoFillBackground(False)
        self.button_choose_image_directory = QPushButton(self.frame)
        self.button_choose_image_directory.setObjectName(u"button_choose_image_directory")
        self.button_choose_image_directory.setEnabled(False)
        self.button_choose_image_directory.setGeometry(QRect(240, 80, 111, 31))
        self.button_choose_image_directory.setAutoFillBackground(False)
        self.label_choose_image_directory = QLabel(self.frame)
        self.label_choose_image_directory.setObjectName(u"label_choose_image_directory")
        self.label_choose_image_directory.setEnabled(False)
        self.label_choose_image_directory.setGeometry(QRect(20, 82, 181, 21))
        self.label_choose_project_name = QLabel(self.frame)
        self.label_choose_project_name.setObjectName(u"label_choose_project_name")
        self.label_choose_project_name.setEnabled(False)
        self.label_choose_project_name.setGeometry(QRect(20, 110, 171, 31))
        self.radiobutton_do_crop = QRadioButton(self.frame)
        self.radiobutton_do_crop.setObjectName(u"radiobutton_do_crop")
        self.radiobutton_do_crop.setEnabled(False)
        self.radiobutton_do_crop.setGeometry(QRect(50, 50, 121, 20))
        self.radiobutton_do_crop.setChecked(True)
        self.radiobutton_do_not_crop = QRadioButton(self.frame)
        self.radiobutton_do_not_crop.setObjectName(u"radiobutton_do_not_crop")
        self.radiobutton_do_not_crop.setEnabled(False)
        self.radiobutton_do_not_crop.setGeometry(QRect(180, 50, 161, 20))
        self.label_crop_images = QLabel(self.frame)
        self.label_crop_images.setObjectName(u"label_crop_images")
        self.label_crop_images.setEnabled(False)
        self.label_crop_images.setGeometry(QRect(20, 50, 21, 16))
        self.input_project_name = QLineEdit(self.frame)
        self.input_project_name.setObjectName(u"input_project_name")
        self.input_project_name.setEnabled(False)
        self.input_project_name.setGeometry(QRect(240, 120, 113, 21))
        self.button_open_project = QPushButton(StartWindow)
        self.button_open_project.setObjectName(u"button_open_project")
        self.button_open_project.setGeometry(QRect(40, 100, 111, 41))
        self.button_open_project.setAutoDefault(True)
        self.label_or = QLabel(StartWindow)
        self.label_or.setObjectName(u"label_or")
        self.label_or.setGeometry(QRect(190, 100, 41, 41))
        font = QFont()
        font.setPointSize(14)
        self.label_or.setFont(font)
        self.label_create_project = QLabel(StartWindow)
        self.label_create_project.setObjectName(u"label_create_project")
        self.label_create_project.setGeometry(QRect(400, 10, 121, 21))
        font1 = QFont()
        font1.setPointSize(12)
        self.label_create_project.setFont(font1)

        self.retranslateUi(StartWindow)

        QMetaObject.connectSlotsByName(StartWindow)
    # setupUi

    def retranslateUi(self, StartWindow):
        StartWindow.setWindowTitle(QCoreApplication.translate("StartWindow", u"CrystalGrowthTool - \u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c", None))
        self.label_choose_project_directory.setText(QCoreApplication.translate("StartWindow", u"1.  \u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0430\u043f\u043a\u0443 \u0434\u043b\u044f \u043f\u0440\u043e\u0435\u043a\u0442\u0430", None))
        self.button_create_project.setText(QCoreApplication.translate("StartWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.button_choose_project_directory.setText(QCoreApplication.translate("StartWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u043f\u043a\u0443", None))
        self.button_choose_image_directory.setText(QCoreApplication.translate("StartWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u043f\u043a\u0443", None))
        self.label_choose_image_directory.setText(QCoreApplication.translate("StartWindow", u"3.  \u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0430\u043f\u043a\u0443 \u0441\u043e \u0441\u043d\u0438\u043c\u043a\u0430\u043c\u0438", None))
        self.label_choose_project_name.setText(QCoreApplication.translate("StartWindow", u"4.  \u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u0430", None))
        self.radiobutton_do_crop.setText(QCoreApplication.translate("StartWindow", u"\u041e\u0431\u0440\u0435\u0437\u0430\u0442\u044c \u0441\u043d\u0438\u043c\u043a\u0438", None))
        self.radiobutton_do_not_crop.setText(QCoreApplication.translate("StartWindow", u"\u0421\u043d\u0438\u043c\u043a\u0438 \u0443\u0436\u0435 \u043e\u0431\u0440\u0435\u0437\u0430\u043d\u044b", None))
        self.label_crop_images.setText(QCoreApplication.translate("StartWindow", u"2.", None))
        self.button_open_project.setText(QCoreApplication.translate("StartWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.label_or.setText(QCoreApplication.translate("StartWindow", u"\u0438\u043b\u0438", None))
        self.label_create_project.setText(QCoreApplication.translate("StartWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
    # retranslateUi

