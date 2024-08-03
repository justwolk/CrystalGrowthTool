import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Signal as pyqtSignal, Slot as pyqtSlot
from PySide6.QtCore import QPoint, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QPixmap, QPainter, QPen, Qt, QPainterPath, QFont, \
    QColor, QIntValidator

from View.start_window import Ui_StartWindow


class StartDialog(QDialog):

    triggerCreateNewProject = pyqtSignal(str, bool, str, str) 
    triggerLoadProject = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._ui = Ui_StartWindow()
        self._ui.setupUi(self)

        self.project_folder = ""

        self.directory = ""
        self.crop = True
        self.image_folder = ""
        self.project_name = ""

        self._ui.openProjectButton.clicked.connect(self.on_open_project_clicked)
        self._ui.chooseProjectDirectoryButton.clicked.connect(self.on_select_project_folder_clicked)
        self._ui.chooseImageDirectory.clicked.connect(self.on_select_image_folder_clicked)

        self._ui.createProjectButton.clicked.connect(self.on_create_project_clicked)
        self._ui.radioButtonCrop.toggled.connect(self.on_radio_button_toggled)
        self._ui.radioButtonDoNotCrop.toggled.connect(self.on_radio_button_toggled)

    def on_select_project_folder_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, 'Откройте директорию для создания проекта')
        if folder != None:
            self.directory = folder
        else:#TODO
            self.close
            
        self._ui.label2.setEnabled(True)
        self._ui.radioButtonCrop.setEnabled(True)
        self._ui.radioButtonDoNotCrop.setEnabled(True)
        self._ui.label3.setEnabled(True)
        self._ui.chooseImageDirectory.setEnabled(True)

    def on_radio_button_toggled(self):
        if self._ui.radioButtonCrop.isChecked():
            self.crop = True
        elif self._ui.radioButtonDoNotCrop.isChecked():
            self.crop = False

    def on_select_image_folder_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, 'Откройте директорию с изображениями')
        if folder != None:
            self.image_folder = folder
        else: #TODO
            self.close

        self._ui.label4.setEnabled(True)
        self._ui.inputProjectName.setEnabled(True)
        self._ui.createProjectButton.setEnabled(True)

    def on_create_project_clicked(self):
        self.project_name = self._ui.inputProjectName.text()
        self.triggerCreateNewProject.emit(self.directory, self.crop, self.image_folder, self.project_name)

    def on_open_project_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, 'Откройте директорию с уже созданным проектом')
        if folder != None:
            self.triggerLoadProject.emit(folder)





