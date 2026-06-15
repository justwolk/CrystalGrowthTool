from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LayerStructureWindow(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.setWindowTitle("Структура ступеней")
        self.model = model
        self.controller = controller
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        button_layout = QHBoxLayout()
        self.add_layer_button = QPushButton("+")
        self.add_layer_button.setFixedSize(30, 30)
        self.add_layer_button.setToolTip("Создать новую пустую ступень")
        self.add_layer_button.clicked.connect(self.create_empty_layer)
        button_layout.addWidget(self.add_layer_button)
        
        self.clear_all_button = QPushButton("Очистить всё")
        self.clear_all_button.setToolTip("Очистить все точки на всех ступенях")
        self.clear_all_button.clicked.connect(self.clear_all_layers)
        button_layout.addWidget(self.clear_all_button)
        
        button_layout.addStretch()
        self.main_layout.addLayout(button_layout)
        
        self.layers_list = QListWidget()
        self.layers_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.layers_list.customContextMenuRequested.connect(self.show_context_menu)
        self.main_layout.addWidget(self.layers_list)
        
        self.layers_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.model.attributeChanged.connect(self.update_layers_list)
        self.controller.update_ui.connect(self.update_layers_list)
        
        self.update_layers_list()
        
        self.resize(300, 400)
    
    def create_empty_layer(self):
        current_crystal = self.model.crystal_object[self.model.current_image]
        current_crystal.growth_lines.append([])
        new_layer_index = len(current_crystal.growth_lines) - 1
        self.controller.go_to_layer(new_layer_index)
        self.controller.update_ui.emit()
    
    def clear_all_layers(self):
        current_crystal = self.model.crystal_object[self.model.current_image]
        
        if not current_crystal.growth_lines:
            QMessageBox.information(self, "Информация", "Нет ступеней для очистки")
            return
        
        total_points = sum(len(layer) for layer in current_crystal.growth_lines)
        if total_points == 0:
            QMessageBox.information(self, "Информация", "Все ступени уже пустые")
            return
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение очистки")
        msg_box.setText(f"Очистить все точки на всех {len(current_crystal.growth_lines)} ступенях?\nВсего будет удалено {total_points} точек.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            for i in range(len(current_crystal.growth_lines)):
                current_crystal.growth_lines[i] = []
            self.controller.update_ui.emit()
        
    def update_layers_list(self, attr_name=None, value=None):
        self.layers_list.clear()
        
        if not self.model.crystal_object or self.model.current_image >= len(self.model.crystal_object):
            return
            
        current_crystal = self.model.crystal_object[self.model.current_image]
        
        if not current_crystal.growth_lines:
            empty_item = QListWidgetItem("Нет ступеней на этом снимке")
            empty_item.setForeground(Qt.gray)
            self.layers_list.addItem(empty_item)
            return
        
        for layer_idx, growth_line in enumerate(current_crystal.growth_lines):
            point_count = len(growth_line) if growth_line else 0
            
            if point_count == 0:
                layer_text = f"Ступень {layer_idx + 1} (пустая)"
            else:
                layer_text = f"Ступень {layer_idx + 1} (точек: {point_count})"
            
            layer_item = QListWidgetItem(layer_text)
            layer_item.setData(Qt.UserRole, layer_idx)
            
            if layer_idx == self.model.current_layer:
                layer_item.setBackground(Qt.yellow)
            
            if point_count == 0:
                layer_item.setForeground(Qt.gray)
            
            self.layers_list.addItem(layer_item)
            
            if growth_line:
                for point_idx, point in enumerate(growth_line):
                    point_type = "Начало" if point_idx == 0 else "Конец" if point_idx == len(growth_line) - 1 else "Точка"
                    point_item = QListWidgetItem(f"    • {point_type} {point_idx + 1}: ({point.x()}, {point.y()})")
                    point_item.setData(Qt.UserRole, -1)
                    self.layers_list.addItem(point_item)
    
    def show_context_menu(self, position):
        item = self.layers_list.itemAt(position)
        if not item:
            return
        
        layer_idx = item.data(Qt.UserRole)
        if layer_idx is None or layer_idx < 0:
            return
        
        menu = QMenu(self)
        clear_action = menu.addAction("Очистить точки")
        delete_action = menu.addAction("Удалить ступень")
        
        action = menu.exec_(self.layers_list.mapToGlobal(position))
        
        if action == clear_action:
            self.clear_layer_points(layer_idx)
        elif action == delete_action:
            self.delete_layer(layer_idx)
    
    def clear_layer_points(self, layer_idx):
        current_crystal = self.model.crystal_object[self.model.current_image]
        if layer_idx >= len(current_crystal.growth_lines):
            return
        
        point_count = len(current_crystal.growth_lines[layer_idx])
        if point_count == 0:
            QMessageBox.information(self, "Информация", "Ступень уже пустая")
            return
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение очистки")
        msg_box.setText(f"Удалить все {point_count} точек на ступени {layer_idx + 1}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            old_layer = self.model.current_layer
            self.controller.go_to_layer(layer_idx)
            self.controller.delete_layer_points()
            
            if old_layer != layer_idx:
                self.controller.go_to_layer(old_layer)
    
    def delete_layer(self, layer_idx):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText(f"Удалить ступень {layer_idx + 1}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            old_layer = self.model.current_layer
            self.controller.go_to_layer(layer_idx)
            self.controller.delete_layer()
            
            if old_layer != layer_idx and old_layer > 0:
                adjusted_layer = old_layer - 1 if old_layer > layer_idx else old_layer
                self.controller.go_to_layer(adjusted_layer)
                
    def on_item_double_clicked(self, item):
        layer_idx = item.data(Qt.UserRole)
        if layer_idx is not None and layer_idx >= 0:
            self.controller.go_to_layer(layer_idx)
            
    def closeEvent(self, event):
        if self.parent():
            event.ignore()
            self.hide()
        else:
            event.accept()
