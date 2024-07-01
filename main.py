import sys
from PySide6.QtWidgets import QApplication
from Model.model import Model
from Controller.controller import Controller
from View.main_view import MainView


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        
        self.model = Model()
        self.main_ctrl = Controller(self.model)
        self.main_view = MainView(self.model, self.main_ctrl)
        self.main_view.show()


if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec())