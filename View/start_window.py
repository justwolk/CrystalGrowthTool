# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'start_window3.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSizePolicy,
    QWidget)

class Ui_StartWindow(object):
    def setupUi(self, StartWindow):
        if not StartWindow.objectName():
            StartWindow.setObjectName(u"StartWindow")
        StartWindow.resize(677, 249)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
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
        self.labelChooseProjectDirectory = QLabel(self.frame)
        self.labelChooseProjectDirectory.setObjectName(u"labelChooseProjectDirectory")
        self.labelChooseProjectDirectory.setGeometry(QRect(20, 4, 191, 41))
        self.createProjectButton = QPushButton(self.frame)
        self.createProjectButton.setObjectName(u"createProjectButton")
        self.createProjectButton.setEnabled(False)
        self.createProjectButton.setGeometry(QRect(140, 150, 111, 31))
        self.createProjectButton.setAutoFillBackground(False)
        self.chooseProjectDirectoryButton = QPushButton(self.frame)
        self.chooseProjectDirectoryButton.setObjectName(u"chooseProjectDirectoryButton")
        self.chooseProjectDirectoryButton.setGeometry(QRect(240, 10, 111, 31))
        self.chooseProjectDirectoryButton.setAutoFillBackground(False)
        self.chooseImageDirectory = QPushButton(self.frame)
        self.chooseImageDirectory.setObjectName(u"chooseImageDirectory")
        self.chooseImageDirectory.setEnabled(False)
        self.chooseImageDirectory.setGeometry(QRect(240, 80, 111, 31))
        self.chooseImageDirectory.setAutoFillBackground(False)
        self.label3 = QLabel(self.frame)
        self.label3.setObjectName(u"label3")
        self.label3.setEnabled(False)
        self.label3.setGeometry(QRect(20, 82, 181, 21))
        self.label4 = QLabel(self.frame)
        self.label4.setObjectName(u"label4")
        self.label4.setEnabled(False)
        self.label4.setGeometry(QRect(20, 110, 171, 31))
        self.radioButtonCrop = QRadioButton(self.frame)
        self.radioButtonCrop.setObjectName(u"radioButtonCrop")
        self.radioButtonCrop.setEnabled(False)
        self.radioButtonCrop.setGeometry(QRect(50, 50, 121, 20))
        self.radioButtonCrop.setChecked(True)
        self.radioButtonDoNotCrop = QRadioButton(self.frame)
        self.radioButtonDoNotCrop.setObjectName(u"radioButtonDoNotCrop")
        self.radioButtonDoNotCrop.setEnabled(False)
        self.radioButtonDoNotCrop.setGeometry(QRect(180, 50, 161, 20))
        self.label2 = QLabel(self.frame)
        self.label2.setObjectName(u"label2")
        self.label2.setEnabled(False)
        self.label2.setGeometry(QRect(20, 50, 21, 16))
        self.inputProjectName = QLineEdit(self.frame)
        self.inputProjectName.setObjectName(u"inputProjectName")
        self.inputProjectName.setEnabled(False)
        self.inputProjectName.setGeometry(QRect(240, 120, 113, 21))
        self.openProjectButton = QPushButton(StartWindow)
        self.openProjectButton.setObjectName(u"openProjectButton")
        self.openProjectButton.setGeometry(QRect(40, 100, 111, 41))
        self.openProjectButton.setAutoDefault(True)
        self.labelOr = QLabel(StartWindow)
        self.labelOr.setObjectName(u"labelOr")
        self.labelOr.setGeometry(QRect(190, 100, 31, 41))
        font = QFont()
        font.setPointSize(14)
        self.labelOr.setFont(font)
        self.labelCreateProject = QLabel(StartWindow)
        self.labelCreateProject.setObjectName(u"labelCreateProject")
        self.labelCreateProject.setGeometry(QRect(400, 10, 121, 21))
        font1 = QFont()
        font1.setPointSize(12)
        self.labelCreateProject.setFont(font1)

        self.retranslateUi(StartWindow)

        QMetaObject.connectSlotsByName(StartWindow)
    # setupUi

    def retranslateUi(self, StartWindow):
        StartWindow.setWindowTitle(QCoreApplication.translate("StartWindow", u"CrystalGrowthTool - \u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c", None))
        self.labelChooseProjectDirectory.setText(QCoreApplication.translate("StartWindow", u"1.  \u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0430\u043f\u043a\u0443 \u0434\u043b\u044f \u043f\u0440\u043e\u0435\u043a\u0442\u0430", None))
        self.createProjectButton.setText(QCoreApplication.translate("StartWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.chooseProjectDirectoryButton.setText(QCoreApplication.translate("StartWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u043f\u043a\u0443", None))
        self.chooseImageDirectory.setText(QCoreApplication.translate("StartWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u043f\u043a\u0443", None))
        self.label3.setText(QCoreApplication.translate("StartWindow", u"3.  \u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0430\u043f\u043a\u0443 \u0441\u043e \u0441\u043d\u0438\u043c\u043a\u0430\u043c\u0438", None))
        self.label4.setText(QCoreApplication.translate("StartWindow", u"4.  \u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u0430", None))
        self.radioButtonCrop.setText(QCoreApplication.translate("StartWindow", u"\u041e\u0431\u0440\u0435\u0437\u0430\u0442\u044c \u0441\u043d\u0438\u043c\u043a\u0438", None))
        self.radioButtonDoNotCrop.setText(QCoreApplication.translate("StartWindow", u"\u0421\u043d\u0438\u043c\u043a\u0438 \u0443\u0436\u0435 \u043e\u0431\u0440\u0435\u0437\u0430\u043d\u044b", None))
        self.label2.setText(QCoreApplication.translate("StartWindow", u"2.", None))
        self.openProjectButton.setText(QCoreApplication.translate("StartWindow", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.labelOr.setText(QCoreApplication.translate("StartWindow", u"\u0438\u043b\u0438", None))
        self.labelCreateProject.setText(QCoreApplication.translate("StartWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
    # retranslateUi

