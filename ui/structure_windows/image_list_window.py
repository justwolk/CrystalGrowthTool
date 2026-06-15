from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide2.QtCore import Qt

class ImageListWindow(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.setWindowTitle("Список снимков")
        self.model = model
        self.controller = controller
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.images_list = QListWidget()
        self.layout.addWidget(self.images_list)
        
        self.images_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.model.attributeChanged.connect(self.update_current_image)
        self.controller.update_ui.connect(self.update_images_list)
        
        self.update_images_list()
        
        self.resize(300, 400)
        
    def update_images_list(self):
        self.images_list.clear()
        for i, photo in enumerate(self.model.photos):
            is_new = i > 0 and self.model.crystal_object[i].not_interacted_image
            text = f"Снимок {i + 1}"
            if is_new:
                text += " (новый)"
            
            item = QListWidgetItem(text)
            if i == self.model.current_image:
                item.setBackground(Qt.yellow)
            self.images_list.addItem(item)
    
    def update_current_image(self, attr_name=None, value=None):
        if attr_name == 'current_image':
            for i in range(self.images_list.count()):
                item = self.images_list.item(i)
                is_new = i > 0 and self.model.crystal_object[i].not_interacted_image
                text = f"Снимок {i + 1}"
                if is_new:
                    text += " (новый)"
                item.setText(text)
                item.setBackground(Qt.yellow if i == value else Qt.white)
    
    def on_item_double_clicked(self, item):
        index = self.images_list.row(item)
        self.controller.go_to_image(index)
        
    def closeEvent(self, event):
        if self.parent():
            event.ignore()
            self.hide()
        else:
            event.accept()
