from PySide2.QtWidgets import QFileDialog, QDialog, QMessageBox
from PySide2.QtCore import Signal as pyqtSignal
from utils.crystal_archive import CrystalArchive
from ui.generated.ui_start_window import Ui_StartWindow
import os


class StartDialog(QDialog):

    triggerCreateNewProject = pyqtSignal(str, bool, str) 
    triggerLoadProject = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._ui = Ui_StartWindow()
        self._ui.setupUi(self)
        
        self.reset_fields()

        self._ui.button_open_project.clicked.connect(self.on_open_project_clicked)
        self._ui.button_choose_project_directory.clicked.connect(self.on_select_project_folder_clicked)
        self._ui.button_choose_image_directory.clicked.connect(self.on_select_image_folder_clicked)
        self._ui.button_create_project.clicked.connect(self.on_create_project_clicked)
        self._ui.radiobutton_do_crop.toggled.connect(self.on_radio_button_toggled)
        self._ui.radiobutton_do_not_crop.toggled.connect(self.on_radio_button_toggled)

    def reset_fields(self):
        self.project_folder = ""
        self.directory = ""
        self.crop = True
        self.image_folder = ""
        self.project_name = ""
        
        self._ui.input_project_name.clear()
        self._ui.input_project_name.setEnabled(False)
        self._ui.button_create_project.setEnabled(False)
        self._ui.label_crop_images.setEnabled(False)
        self._ui.radiobutton_do_crop.setEnabled(False)
        self._ui.radiobutton_do_not_crop.setEnabled(False)
        self._ui.radiobutton_do_crop.setChecked(True)
        self._ui.label_choose_image_directory.setEnabled(False)
        self._ui.button_choose_image_directory.setEnabled(False)
        self._ui.label_choose_project_name.setEnabled(False)

    def showEvent(self, event):
        super().showEvent(event)
        self.reset_fields()

    def on_select_project_folder_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для создания проекта")
        if folder:
            self.directory = folder
            self._ui.label_crop_images.setEnabled(True)
            self._ui.radiobutton_do_crop.setEnabled(True)
            self._ui.radiobutton_do_not_crop.setEnabled(True)
            self._ui.label_choose_image_directory.setEnabled(True)
            self._ui.button_choose_image_directory.setEnabled(True)
        else:
            self.show_error_message("Папка для проекта не выбрана")

    def on_select_image_folder_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку с изображениями")
        if folder:
            images = [file for file in os.listdir(folder) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not images:
                self.show_error_message("Папка с изображениями не выбрана или не содержит изображений")
                return
            self.image_folder = folder
            self._ui.label_choose_project_name.setEnabled(True)
            self._ui.input_project_name.setEnabled(True)
            self._ui.button_create_project.setEnabled(True)
        else:
            self.show_error_message("Папка с изображениями не выбрана")

    def on_create_project_clicked(self):
        self.project_name = self._ui.input_project_name.text().strip()
        if not self.project_name:
            self.show_error_message("Имя проекта не может быть пустым")
            return

        archive = CrystalArchive()
        crystal_file_path, _ = archive.generate_unique_path(
            self.directory, 
            self.project_name
        )

        self.triggerCreateNewProject.emit(crystal_file_path, self.crop, self.image_folder)

    def on_open_project_clicked(self):
        file, _ = QFileDialog.getOpenFileName(self, "Открыть файл проекта", '', 'Crystal Project Files (*.crystal)')
        if file:
            self.triggerLoadProject.emit(file)
        else:
            self.show_error_message("Файл проекта не выбран")

    def on_radio_button_toggled(self):
        if self._ui.radiobutton_do_crop.isChecked():
            self.crop = True
        elif self._ui.radiobutton_do_not_crop.isChecked():
            self.crop = False

    def show_error_message(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Ошибка")
        error_box.setText(message)
        error_box.exec_()
