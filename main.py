import sys
from PySide6.QtWidgets import QApplication
from Model.model import Model
from Controller.controller import Controller
from View.main_view import MainView
from View.start_window_view import StartDialog

class App(QApplication):

    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        self.start_dialog = StartDialog()
        self.start_dialog.triggerLoadProject.connect(self.load_project)
        self.start_dialog.triggerCreateNewProject.connect(self.create_project)
        self.start_dialog.show()
        self.model = None

    def load_project(self, project_folder):
        self.model = Model(project_folder)
        self.launch_main_view()

    def create_project(self, project_folder, do_crop, image_folder, project_name):
        self.model = Model(project_folder, do_crop, image_folder, project_name)
        self.launch_main_view()

    def launch_main_view(self):
        self.start_dialog.close()
        self.main_ctrl = Controller(self.model)
        self.main_view = MainView(self.model, self.main_ctrl)
        self.main_view.show()

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec_())
