import copy
import os
import tempfile

from PySide2.QtCore import QPoint, QPointF, QObject, Qt, QTimer
from PySide2.QtCore import Signal as pyqtSignal, Slot as pyqtSlot
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QMessageBox

from controllers.commands import (
    AddGridLinePointCommand,
    AddGrowthLinePointCommand,
    ClearAllPointsCommand,
    ClearAllPointsEverywhereCommand,
    CommandManager,
    DeleteGridLinePointCommand,
    DeleteGrowthLinePointCommand,
    DeleteLayerCommand,
    DeleteLayerPointsCommand,
    GenerateIntersectionsCommand,
    InsertGridLinePointBetweenCommand,
    InsertGrowthLinePointBetweenCommand,
    MoveGridLinePointCommand,
    MoveGrowthLinePointCommand,
)
from controllers.interaction_modes import InteractionMode, MovePointMode
from model.crystal_image import CrystalImage
from utils.save_in_excel import save_in_excel as export_project_to_excel
from utils.grid_generator import build_grid_lines
from utils.crop_images import init_images as prepare_images


class MainController(QObject):
    update_ui = pyqtSignal()
    update_image2 = pyqtSignal()  # быстрый сигнал только для image2
    modeChanged = pyqtSignal(int)

    def __init__(self, model):
        super().__init__()
        self._model = model
        self.mode = InteractionMode.SELECT_CENTER
        self.selected_grow_line_point_to_move = None
        self.move_point_mode = MovePointMode.DRAG_AND_DROP
        self._dragging_layer_point = False
        self._dragged_point_index = None
        self._drag_start_point = None 
        self._drag_preview_point = None 
        self._drag_timer = QTimer()
        self._drag_timer.setInterval(1000 // 60) # 60 fps частота обновления во время drag
        self._drag_timer.timeout.connect(self._on_drag_timer)
        
        self._alt_mode_active = False
        self._alt_selected_point_index1 = None
        self._alt_selected_point_index2 = None
        
        self._command_manager = CommandManager()
        
        self._model.attributeChanged.connect(self._on_model_attribute_changed)

    def _on_model_attribute_changed(self, name, value):
        if name in ('center_x', 'center_y'):
            if self._model.crystal_object and 0 <= self._model.current_image < len(self._model.crystal_object):
                crystal = self._model.crystal_object[self._model.current_image]
                setattr(crystal, name, value)
                self.update_image2.emit()

    def undo(self):
        if self._command_manager.undo():
            self.update_ui.emit()
    
    def redo(self):
        if self._command_manager.redo():
            self.update_ui.emit()
    
    def can_undo(self):
        return self._command_manager.can_undo()
    
    def can_redo(self):
        return self._command_manager.can_redo()
    
    def _execute_command(self, command):
        self._command_manager.execute_command(command)
    
    def save_project(self):
        self._model.save_to_crystal()
    
    @pyqtSlot(int)
    def set_mode(self, mode):
        if isinstance(mode, int):
            try:
                new_mode = InteractionMode(mode)
            except ValueError:
                new_mode = InteractionMode.SELECT_CENTER
        elif isinstance(mode, InteractionMode):
            new_mode = mode
        else:
            new_mode = InteractionMode.SELECT_CENTER
        
        if self.mode != new_mode:
            self.mode = new_mode
            self.modeChanged.emit(self.mode.value)

    def clear_all_points_on_image(self):
        command = ClearAllPointsCommand(self._model, self.update_ui.emit)
        self._execute_command(command)

    def clear_all_points_everywhere(self):
        command = ClearAllPointsEverywhereCommand(self._model, self.update_ui.emit)
        self._execute_command(command)

    def on_reverse_ui_toggled(self):
        self._model.ui_enabled = not self._model.ui_enabled

    @pyqtSlot(int)
    def go_to_image(self, target_image):
        total_images = len(self._model.crystal_object)
        current_image = self._model.current_image
        
        if not (0 <= target_image <= total_images - 1):
            return
        
        previous_image = current_image
        self._model.update_attribute('current_image', target_image)
        
        target_crystal = self._model.crystal_object[target_image]
        
        if target_crystal.not_interacted_image and target_image > 0:
            self._handle_new_image_interaction(previous_image, target_image)
        
        if target_crystal.center_x is not None and target_crystal.center_y is not None:
            self._model.update_attribute('center_x', target_crystal.center_x)
            self._model.update_attribute('center_y', target_crystal.center_y)
        elif self._model.center_x is not None and self._model.center_y is not None:
            target_crystal.center_x = self._model.center_x
            target_crystal.center_y = self._model.center_y

        self.update_ui.emit()
    
    def _handle_new_image_interaction(self, source_image, target_image):
        source_crystal = self._model.crystal_object[source_image]
        target_crystal = self._model.crystal_object[target_image]
        
        target_crystal.set_interacted()

        if target_crystal.center_x is None:
            target_crystal.center_x = source_crystal.center_x
            target_crystal.center_y = source_crystal.center_y
        
        if self._model.checkbox_ask_new_image_copy:
            choice = self._show_copy_dialog()
            
            if choice in ('both', 'layers'):
                self._copy_layers(source_crystal, target_crystal)
            if choice in ('both', 'grid'):
                self._copy_grid(source_crystal, target_crystal)
        else:
            if self._model.checkbox_copy_layers:
                self._copy_layers(source_crystal, target_crystal)
            if self._model.checkbox_copy_grid:
                self._copy_grid(source_crystal, target_crystal)

    def _show_copy_dialog(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Новый снимок")
        msg_box.setText("Что скопировать с предыдущего снимка?")

        copy_both = msg_box.addButton("Сетку и ступени", QMessageBox.AcceptRole)
        copy_grid = msg_box.addButton("Только сетку", QMessageBox.AcceptRole)
        copy_layers = msg_box.addButton("Только ступени", QMessageBox.AcceptRole)
        skip = msg_box.addButton("Ничего", QMessageBox.RejectRole)
        msg_box.setDefaultButton(copy_both)

        msg_box.exec_()
        clicked_button = msg_box.clickedButton()

        if clicked_button == copy_both:
            return 'both'
        if clicked_button == copy_grid:
            return 'grid'
        if clicked_button == copy_layers:
            return 'layers'
        if clicked_button == skip:
            return 'none'
        return 'none'

    def _copy_layers(self, source_crystal, target_crystal):
        if not target_crystal.growth_lines:
            target_crystal.growth_lines = copy.deepcopy(source_crystal.growth_lines)

    def _copy_grid(self, source_crystal, target_crystal):
        if not target_crystal.grid_lines:
            target_crystal.grid_lines = copy.deepcopy(source_crystal.grid_lines)
            target_crystal.center_x = source_crystal.center_x
            target_crystal.center_y = source_crystal.center_y

    @pyqtSlot(int)
    def go_to_layer(self, target_layer):
        current_image = self._model.current_image
        crystal_object = self._model.crystal_object[current_image]

        if target_layer < 0:
            return
        
        max_allowed_layer = len(crystal_object.growth_lines)
        
        if target_layer > max_allowed_layer:
            QMessageBox.warning(
                None, 
                "Ошибка", 
                f"Нельзя перейти на ступень {target_layer + 1}.\nМожно создать только следующую ступень {max_allowed_layer + 1}."
            )
            return
        
        if target_layer == max_allowed_layer:
            crystal_object.growth_lines.append([])
        
        self._model.update_attribute('current_layer', target_layer)
        self.update_ui.emit()
    
    @pyqtSlot(int)
    def go_to_grid_line(self, target_line):
        current_image = self._model.current_image
        crystal_object = self._model.crystal_object[current_image]

        if target_line < 0:
            return
        
        max_allowed_line = len(crystal_object.grid_lines)
        
        if target_line > max_allowed_line:
            QMessageBox.warning(
                None, 
                "Ошибка", 
                f"Нельзя перейти на линию {target_line + 1}.\nМожно создать только следующую линию {max_allowed_line + 1}."
            )
            return
        
        if target_line == max_allowed_line:
            crystal_object.grid_lines.append([])
        
        self._model.update_attribute('current_grid_line', target_line)
        self.update_ui.emit()

    def go_next_image(self):
        self.go_to_image(self._model.current_image + 1)

    def go_previous_image(self):
        self.go_to_image(self._model.current_image - 1)

    def go_next_layer(self):
        self.go_to_layer(self._model.current_layer + 1)

    def go_previous_layer(self):
        self.go_to_layer(self._model.current_layer - 1)
    
    def go_next_grid_line(self):
        self.go_to_grid_line(self._model.current_grid_line + 1)

    def go_previous_grid_line(self):
        self.go_to_grid_line(self._model.current_grid_line - 1)

    @pyqtSlot()
    def delete_layer(self):
        command = DeleteLayerCommand(self._model, self.update_ui.emit)
        self._execute_command(command)

    @pyqtSlot()
    def delete_layer_points(self):
        command = DeleteLayerPointsCommand(self._model, self.update_ui.emit)
        self._execute_command(command)

    def save_to_excel(self):
        export_project_to_excel(self._model)

    def apply_center_position(self, x, y):
        self._model.center_x = x
        self._model.center_y = y

    @pyqtSlot(str)
    def crop_images(self, folder_path):
        temp_dir = tempfile.mkdtemp(prefix='crystal_crop_')
        
        try:
            cropped_images = prepare_images(folder_path, do_crop=True)
            
            for idx, img in enumerate(cropped_images):
                img_path = os.path.join(temp_dir, f'img_{idx + 1}.png')
                img.save(img_path)
            
            self.image_folder_selected(temp_dir)
            
        except Exception as e:
            print(f"Ошибка обрезки изображений: {e}")

    @pyqtSlot(str)
    def image_folder_selected(self, folder_path):
        self._model.image_folder = folder_path
        files = os.listdir(folder_path)
        # отфильтровать и отсортировать картинки
        photos = [file for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png'))]
        photos.sort()
        self._model.crystal_object = [CrystalImage(photo_path) for photo_path in photos]
        self._model.photos = photos

    @pyqtSlot()
    def create_grid_for_current_image(self):
        current_image = self._model.current_image
        crystal_object = self._model.crystal_object[current_image]
        
        if current_image < len(self._model.photos):
            photo_path = os.path.join(self._model.image_folder, self._model.photos[current_image])
            pixmap = QPixmap(photo_path)
            
            lines = build_grid_lines(
                self._model.grid_type, 
                pixmap.width(), 
                pixmap.height(), 
                self._model.division_count, 
                QPointF(self._model.center_x, self._model.center_y),
                self._model.tilt, 
                self._model.grid_scale, 
                self._model.ellipse_width,
                self._model.ellipse_height,
            )
            
            crystal_object.center_x = self._model.center_x
            crystal_object.center_y = self._model.center_y
            
            crystal_object.set_grid_lines(lines)
            self.update_ui.emit()
    
    @pyqtSlot()
    def delete_grid_for_current_image(self):
        current_image = self._model.current_image
        crystal_object = self._model.crystal_object[current_image]
        crystal_object.clear_grid_lines()
        self.update_ui.emit()
    
    @pyqtSlot()
    def copy_grid_to_all_next(self):
        current_image = self._model.current_image
        source_crystal = self._model.crystal_object[current_image]
        
        if not source_crystal.grid_lines:
            QMessageBox.warning(None, "Предупреждение", "На текущем снимке нет сетки для копирования")
            return
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Копирование сетки")
        msg_box.setText(f"Скопировать сетку с текущего снимка на все последующие (с {current_image + 1} по {len(self._model.crystal_object)})?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        
        if msg_box.exec_() == QMessageBox.Yes:
            for i in range(current_image + 1, len(self._model.crystal_object)):
                target_crystal = self._model.crystal_object[i]
                target_crystal.grid_lines = copy.deepcopy(source_crystal.grid_lines)
            
            self.update_ui.emit()
            QMessageBox.information(None, "Готово", f"Сетка скопирована на {len(self._model.crystal_object) - current_image - 1} снимков")
    
    @pyqtSlot()
    def delete_all_grids(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Удаление всех сеток")
        msg_box.setText("Удалить все сетки на всех снимках?")
        msg_box.setInformativeText("Это действие нельзя отменить!")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            for crystal_obj in self._model.crystal_object:
                crystal_obj.clear_grid_lines()
            
            self.update_ui.emit()
            QMessageBox.information(None, "Готово", "Все сетки удалены")
    
    @pyqtSlot()
    def copy_grid_from_previous(self):
        current_image = self._model.current_image
        
        if current_image == 0:
            QMessageBox.warning(None, "Предупреждение", "Это первый снимок, нет предыдущего снимка")
            return
        
        source_crystal = self._model.crystal_object[current_image - 1]
        
        if not source_crystal.grid_lines:
            QMessageBox.warning(None, "Предупреждение", "На предыдущем снимке нет сетки для копирования")
            return
        
        target_crystal = self._model.crystal_object[current_image]
        target_crystal.grid_lines = copy.deepcopy(source_crystal.grid_lines)
        
        self.update_ui.emit()
        QMessageBox.information(None, "Готово", "Сетка скопирована с предыдущего снимка")
    
    def get_current_grid_lines(self):
        current_image = self._model.current_image
        if current_image < len(self._model.crystal_object):
            return self._model.crystal_object[current_image].grid_lines
        return []
    
    @pyqtSlot()
    def generate_intersections_for_current_layer(self):
        command = GenerateIntersectionsCommand(self._model, 'layer', self.update_ui.emit)
        command.set_grid_lines(self.get_current_grid_lines())
        self._execute_command(command)

    @pyqtSlot()
    def generate_intersections_for_current_image(self):
        command = GenerateIntersectionsCommand(self._model, 'image', self.update_ui.emit)
        command.set_grid_lines(self.get_current_grid_lines())
        self._execute_command(command)

    @pyqtSlot()
    def generate_intersections_for_all_images(self):
        command = GenerateIntersectionsCommand(self._model, 'all', self.update_ui.emit)
        command.set_grid_lines(self.get_current_grid_lines())
        self._execute_command(command)

    def convert_click_to_image_coords(self, click_pos, original_size, current_size, scale=1.0, base_scale=1.0, offset=QPoint(0, 0), clamp_to_image=False):
        orig_w, orig_h = original_size.width(), original_size.height()
        widget_w, widget_h = current_size.width(), current_size.height()

        total_scale = base_scale * scale
        offset_x = (widget_w - int(orig_w * total_scale)) // 2 + offset.x()
        offset_y = (widget_h - int(orig_h * total_scale)) // 2 + offset.y()

        img_x = (click_pos.x() - offset_x) / total_scale
        img_y = (click_pos.y() - offset_y) / total_scale

        if clamp_to_image:
            img_x = max(0, min(orig_w - 1, img_x))
            img_y = max(0, min(orig_h - 1, img_y))

        return QPointF(img_x, img_y)


    def handle_mouse_click(self, event, original_size, current_size, scale=1.0, base_scale=1.0, offset=QPoint(0, 0)):
        click_pos = self.convert_click_to_image_coords(
            event.pos(), original_size, current_size, scale, base_scale, offset
        )

        current_image = self._model.current_image
        current_layer = self._model.current_layer
        crystal_object = self._model.crystal_object[current_image]

        if event.button() == Qt.LeftButton:
            self._handle_left_click(click_pos, crystal_object, current_layer)

    def _handle_left_click(self, click_pos, crystal_object, current_layer):
        if self.selected_grow_line_point_to_move is not None and self.mode != InteractionMode.MOVE_POINT:
            self.selected_grow_line_point_to_move = None

        if self.mode == InteractionMode.SELECT_CENTER:
            self.apply_center_position(click_pos.x(), click_pos.y())

        elif self.mode == InteractionMode.ADD_POINT:
            if self._model.work_with_grid_mode:
                self._add_grid_point(click_pos)
            else:
                command = AddGrowthLinePointCommand(self._model, click_pos, self.update_ui.emit)
                self._execute_command(command)

        elif self.mode == InteractionMode.DELETE_POINT:
            if self._model.work_with_grid_mode:
                self._delete_grid_point(click_pos, crystal_object)
            else:
                command = DeleteGrowthLinePointCommand(self._model, click_pos, self.update_ui.emit)
                self._execute_command(command)

        elif self.mode == InteractionMode.MOVE_POINT:
            if self._model.work_with_grid_mode:
                self._handle_move_grid_point(click_pos, crystal_object)
            else:
                self._handle_move_point(click_pos, crystal_object, current_layer)
    
    def _add_grid_point(self, click_pos):
        current_line = self._model.current_grid_line
        
        command = AddGridLinePointCommand(self._model, click_pos, current_line, self.update_ui.emit)
        self._execute_command(command)
    
    def _delete_grid_point(self, click_pos, crystal_object):
        current_line = self._model.current_grid_line
        if current_line >= len(crystal_object.grid_lines):
            return
        
        points = crystal_object.grid_lines[current_line]
        if not points:
            return
        
        click_threshold = 100
        closest_point = None
        min_distance = float('inf')
        
        for point in points:
            distance = (point - click_pos).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                closest_point = point
        
        if min_distance <= click_threshold and closest_point is not None:
            command = DeleteGridLinePointCommand(self._model, closest_point, current_line, self.update_ui.emit)
            self._execute_command(command)
    
    def _handle_move_grid_point(self, click_pos, crystal_object):
        current_line = self._model.current_grid_line
        if current_line >= len(crystal_object.grid_lines):
            return
        
        points = crystal_object.grid_lines[current_line]
        if not points:
            return

        if self.move_point_mode == MovePointMode.CLICK_TO_MOVE:
            if self.selected_grow_line_point_to_move is not None:
                old_point = self.selected_grow_line_point_to_move
                command = MoveGridLinePointCommand(self._model, old_point, click_pos, current_line, self.update_ui.emit)
                self._execute_command(command)
                
                self.selected_grow_line_point_to_move = None
            else:
                self.selected_grow_line_point_to_move = click_pos

    def _handle_move_point(self, click_pos, crystal_object, current_layer):
        points = crystal_object.growth_lines[current_layer] if len(crystal_object.growth_lines) > current_layer else []
        if not points:
            return

        if self.move_point_mode == MovePointMode.CLICK_TO_MOVE:
            if self.selected_grow_line_point_to_move is not None:
                command = MoveGrowthLinePointCommand(
                    self._model, self.selected_grow_line_point_to_move, click_pos, self.update_ui.emit
                )
                self._execute_command(command)
                self.selected_grow_line_point_to_move = None
            else:
                self.selected_grow_line_point_to_move = click_pos

    def handle_drag_and_drop(self, event_type, event, original_size, current_size, scale=1.0, base_scale=1.0, offset=QPoint(0, 0)):
        if self.mode != InteractionMode.MOVE_POINT or self.move_point_mode != MovePointMode.DRAG_AND_DROP:
            return

        click_pos = self.convert_click_to_image_coords(
            event.pos(), original_size, current_size, scale, base_scale, offset
        )
        
        current_image = self._model.current_image
        crystal_object = self._model.crystal_object[current_image]
        
        if self._model.work_with_grid_mode:
            current_line = self._model.current_grid_line
            points = crystal_object.grid_lines[current_line] if current_line < len(crystal_object.grid_lines) else []
        else:
            current_layer = self._model.current_layer
            points = crystal_object.growth_lines[current_layer] if current_layer < len(crystal_object.growth_lines) else []
        
        if event_type == 'press' and event.button() == Qt.LeftButton:
            self._start_drag(click_pos, points)
            
        elif event_type == 'move' and self._dragging_layer_point:
            self._update_drag_preview(click_pos)
            
        elif event_type == 'release' and self._dragging_layer_point:
            self._finish_drag(click_pos)
    
    def _start_drag(self, click_pos, points):
        if not points:
            return
            
        click_threshold = 100
        min_distance = float('inf')
        closest_index = None
        
        for i, point in enumerate(points):
            distance = (point - click_pos).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                closest_index = i
                
        if min_distance < click_threshold and closest_index is not None:
            self._dragging_layer_point = True
            self._dragged_point_index = closest_index
            self._drag_start_point = QPointF(points[closest_index])
            self._drag_preview_point = QPointF(points[closest_index])
            self._drag_timer.start()

    def _update_drag_preview(self, click_pos):
        if self._dragged_point_index is not None:
            self._drag_preview_point = QPointF(click_pos)

    def _finish_drag(self, click_pos):
        if self._dragged_point_index is not None and self._drag_start_point is not None:
            if (click_pos.x() != self._drag_start_point.x() or 
                click_pos.y() != self._drag_start_point.y()):
                
                if self._model.work_with_grid_mode:
                    current_image = self._model.current_image
                    current_line = self._model.current_grid_line
                    crystal_object = self._model.crystal_object[current_image]
                    
                    if current_line < len(crystal_object.grid_lines):
                         command = MoveGridLinePointCommand(
                             self._model, self._drag_start_point, click_pos, current_line, self.update_ui.emit
                         )
                         self._execute_command(command)
                else:
                    command = MoveGrowthLinePointCommand(
                        self._model, self._drag_start_point, click_pos, self.update_ui.emit
                    )
                    self._execute_command(command)
                
        self._dragging_layer_point = False
        self._dragged_point_index = None
        self._drag_start_point = None
        self._drag_preview_point = None
        self._drag_timer.stop()
        self.update_ui.emit()

    def set_alt_mode(self, active):
        self._alt_mode_active = active
        if not active:
            self._alt_selected_point_index1 = None
            self._alt_selected_point_index2 = None
        self.update_ui.emit()
    
    def handle_alt_mode_click(self, click_pos, original_size, current_size, scale=1.0, base_scale=1.0, offset=QPoint(0, 0)):
        if not self._alt_mode_active:
            return
        
        image_click_pos = self.convert_click_to_image_coords(
            click_pos, original_size, current_size, scale, base_scale, offset
        )
        
        current_image = self._model.current_image
        crystal_object = self._model.crystal_object[current_image]
        
        if self._model.work_with_grid_mode:
            current_line = self._model.current_grid_line
            if current_line >= len(crystal_object.grid_lines):
                return
            points = crystal_object.grid_lines[current_line]
        else:
            current_layer = self._model.current_layer
            if current_layer >= len(crystal_object.growth_lines):
                return
            points = crystal_object.growth_lines[current_layer]
        
        if not points:
            return
        
        nearest_index = self._find_nearest_point_index(image_click_pos, points)
        if nearest_index is None:
            return
        
        if self._alt_selected_point_index1 is None:
            self._alt_selected_point_index1 = nearest_index
            self.update_ui.emit()
        elif self._alt_selected_point_index2 is None:
            if nearest_index == self._alt_selected_point_index1:
                return
            
            idx1 = self._alt_selected_point_index1
            idx2 = nearest_index
            
            if abs(idx1 - idx2) != 1:
                print("Ошибка: точки должны быть соседними")
                self._alt_selected_point_index1 = None
                self.update_ui.emit()
                return
            
            self._alt_selected_point_index2 = idx2
            self._insert_point_between(idx1, idx2)
            
            self._alt_selected_point_index1 = None
            self._alt_selected_point_index2 = None
            self.update_ui.emit()
    
    def _find_nearest_point_index(self, click_pos, points):
        click_threshold = 100
        min_distance = float('inf')
        nearest_index = None
        
        for i, point in enumerate(points):
            distance = (point - click_pos).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                nearest_index = i
        
        if min_distance <= click_threshold:
            return nearest_index
        return None
    
    def _insert_point_between(self, idx1, idx2):
        if self._model.work_with_grid_mode:
            current_line = self._model.current_grid_line
            command = InsertGridLinePointBetweenCommand(
                self._model, current_line, idx1, idx2, self.update_ui.emit
            )
        else:
            command = InsertGrowthLinePointBetweenCommand(
                self._model, idx1, idx2, self.update_ui.emit
            )
        self._execute_command(command)
    
    def get_alt_mode_state(self):
        return {
            'active': self._alt_mode_active,
            'selected_index1': self._alt_selected_point_index1,
            'selected_index2': self._alt_selected_point_index2
        }

    def _on_drag_timer(self):
        if self._dragging_layer_point:
            self.update_image2.emit()
        else:
            self._drag_timer.stop()
