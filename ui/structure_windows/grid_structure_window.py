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


class GridStructureWindow(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.setWindowTitle("Структура сетки")
        self.model = model
        self.controller = controller
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        button_layout = QHBoxLayout()
        self.add_line_button = QPushButton("+")
        self.add_line_button.setFixedSize(30, 30)
        self.add_line_button.setToolTip("Создать новую пустую линию сетки")
        self.add_line_button.clicked.connect(self.create_empty_line)
        button_layout.addWidget(self.add_line_button)
        
        self.clear_all_button = QPushButton("Очистить всё")
        self.clear_all_button.setToolTip("Очистить все точки на всех линиях")
        self.clear_all_button.clicked.connect(self.clear_all_lines)
        button_layout.addWidget(self.clear_all_button)
        
        button_layout.addStretch()
        self.main_layout.addLayout(button_layout)
        
        self.grid_list = QListWidget()
        self.grid_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid_list.customContextMenuRequested.connect(self.show_context_menu)
        self.main_layout.addWidget(self.grid_list)
        
        self.grid_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.model.attributeChanged.connect(self.update_grid_info)
        self.controller.update_ui.connect(self.update_grid_info)
        
        self.update_grid_info()
        
        self.resize(400, 500)

    def create_empty_line(self):
        current_crystal = self.model.crystal_object[self.model.current_image]
        current_crystal.grid_lines.append([])
        self.update_grid_info()
        self._trigger_redraw()
    
    def clear_all_lines(self):
        current_crystal = self.model.crystal_object[self.model.current_image]
        
        if not current_crystal.grid_lines:
            QMessageBox.information(self, "Информация", "Нет линий для очистки")
            return
        
        total_points = sum(len(line) for line in current_crystal.grid_lines)
        if total_points == 0:
            QMessageBox.information(self, "Информация", "Все линии уже пустые")
            return
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение очистки")
        msg_box.setText(f"Очистить все точки на всех {len(current_crystal.grid_lines)} линиях?\nВсего будет удалено {total_points} точек.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            for i in range(len(current_crystal.grid_lines)):
                current_crystal.grid_lines[i] = []
            self.update_grid_info()
            self._trigger_redraw()
    
    def update_grid_info(self, attr_name=None, value=None):
        self.grid_list.clear()
        
        current_crystal = self.model.crystal_object[self.model.current_image]
        lines = current_crystal.grid_lines
        
        if not lines:
            empty_item = QListWidgetItem("Нет линий сетки на этом снимке")
            empty_item.setForeground(Qt.gray)
            self.grid_list.addItem(empty_item)
            return
        
        for idx, line in enumerate(lines):
            point_count = len(line) if line else 0
            
            if point_count == 0:
                line_text = f"Линия {idx + 1} (пустая)"
            elif point_count == 2:
                line_text = f"Линия {idx + 1} (заполнена)"
            else:
                line_text = f"Линия {idx + 1} (точек: {point_count})"
            
            line_item = QListWidgetItem(line_text)
            line_item.setData(Qt.UserRole, idx)
            
            if idx == self.model.current_grid_line:
                line_item.setBackground(Qt.yellow)
            
            if point_count == 0:
                line_item.setForeground(Qt.gray)
            
            self.grid_list.addItem(line_item)
            
            if line:
                for point_idx, point in enumerate(line):
                    point_type = "Начало" if point_idx == 0 else "Конец" if point_idx == len(line) - 1 else "Точка"
                    point_item = QListWidgetItem(f"    • {point_type} {point_idx + 1}: ({int(point.x())}, {int(point.y())})")
                    point_item.setData(Qt.UserRole, -1)
                    self.grid_list.addItem(point_item)
    
    def show_context_menu(self, position):
        item = self.grid_list.itemAt(position)
        if not item:
            return
        
        line_idx = item.data(Qt.UserRole)
        if line_idx is None or line_idx < 0:
            return
        
        menu = QMenu(self)
        clear_action = menu.addAction("Очистить точки")
        delete_action = menu.addAction("Удалить линию")
        
        action = menu.exec_(self.grid_list.mapToGlobal(position))
        
        if action == clear_action:
            self.clear_line_points(line_idx)
        elif action == delete_action:
            self.delete_line(line_idx)
    
    def clear_line_points(self, line_idx):
        current_crystal = self.model.crystal_object[self.model.current_image]
        
        if line_idx >= len(current_crystal.grid_lines):
            return
        
        point_count = len(current_crystal.grid_lines[line_idx])
        if point_count == 0:
            QMessageBox.information(self, "Информация", "Линия уже пустая")
            return
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение очистки")
        msg_box.setText(f"Удалить все {point_count} точек на линии {line_idx + 1}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            current_crystal.grid_lines[line_idx] = []
            self.update_grid_info()
            self._trigger_redraw()
    
    def delete_line(self, line_idx):
        current_crystal = self.model.crystal_object[self.model.current_image]
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText(f"Удалить линию {line_idx + 1}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            if line_idx < len(current_crystal.grid_lines):
                del current_crystal.grid_lines[line_idx]
            self.update_grid_info()
            self._trigger_redraw()
    
    def _trigger_redraw(self):
        self.model.attributeChanged.emit('grid_lines', None)
    
    def on_item_double_clicked(self, item):
        line_idx = item.data(Qt.UserRole)
        if line_idx is not None and line_idx >= 0:
            self.model.update_attribute('current_grid_line', line_idx)
        
    def closeEvent(self, event):
        if self.parent(): 
            event.ignore()
            self.hide()
        else:
            event.accept()
