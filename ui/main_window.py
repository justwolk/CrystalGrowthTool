import os
import re
import sys

from PySide2.QtCore import (
    QEvent, QPoint, Qt, QTimer, QUrl,
    Signal as pyqtSignal, Slot as pyqtSlot
)
from PySide2.QtGui import (
    QDesktopServices, QKeySequence
) 
from PySide2.QtWidgets import (
    QApplication, QFileDialog, QKeySequenceEdit, QLineEdit, 
    QMainWindow, QMessageBox, QShortcut, QActionGroup
)

from controllers.interaction_modes import InteractionMode
from utils.grid_generator import GridType
from ui.generated.ui_main_window import Ui_MainWindow
from ui.hotkeys import HotkeyController, HotkeyManager
from ui.image_rendering import ImageRenderingMixin
from ui.image_viewport_state import ImageViewportState
from ui.structure_windows.grid_structure_window import GridStructureWindow
from ui.structure_windows.image_list_window import ImageListWindow
from ui.structure_windows.layer_structure_window import LayerStructureWindow


class MainWindow(ImageRenderingMixin, QMainWindow):
    projectClosed = pyqtSignal()
    projectOpenRequested = pyqtSignal(str)

    def __init__(self, model, main_controller):
        super().__init__()
        self._shortcuts = {}
        self._model = model
        self._main_controller = main_controller
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        
        self._image2_handler = ImageViewportState()
        
        self._last_valid_layer_number = self._model.current_layer + 1
        self._last_valid_image_number = self._model.current_image + 1

        self._force_close = False
        
        self._init_hotkeys()
        self._init_extra_windows()
        self._init_autosave_timer()
        self._init_ui_connections()
        self._init_model_connections()
        self._init_shortcuts()
        self._setup_image_layout()
        
        self._update_window_title()
        self.localize_ui()
        self.draw_ui_images()
        
        self._init_slider_sync()
    
    def _init_hotkeys(self):
        self.hotkey_manager = HotkeyManager()
        self.hotkey_controller = HotkeyController(self, self.hotkey_manager)
    
    def _init_extra_windows(self):
        self.layers_window = LayerStructureWindow(self._model, self._main_controller)
        self.images_window = ImageListWindow(self._model, self._main_controller)
        self.grid_window = GridStructureWindow(self._model, self._main_controller)
        
        self._ui.label_layer_input.mousePressEvent = self._show_layers_window
        self._ui.label_image_number.mousePressEvent = self._show_images_window
        self._ui.button_show_grid_line_structure.clicked.connect(self._show_grid_window)
    
    def _show_layers_window(self, event):
        if self.layers_window.isHidden():
            self.layers_window.show()
        self.layers_window.raise_()
        self.layers_window.activateWindow()

    def _show_images_window(self, event):
        if self.images_window.isHidden():
            self.images_window.show()
        self.images_window.raise_()
        self.images_window.activateWindow()

    def _show_grid_window(self):
        if self.grid_window.isHidden():
            self.grid_window.show()
        self.grid_window.raise_()
        self.grid_window.activateWindow()

    def _setup_image_layout(self):
        from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QSizePolicy, QWidget
        
        if self._ui.CentralWidget.layout() is None:
            central_layout = QVBoxLayout(self._ui.CentralWidget)
            central_layout.setContentsMargins(5, 5, 5, 5)
            central_layout.setSpacing(5)
            
            toolbar_container = QWidget()
            toolbar_layout = QHBoxLayout(toolbar_container)
            toolbar_layout.setContentsMargins(0, 0, 0, 0)
            toolbar_layout.setSpacing(5)
            
            toolbar_widgets = [
                self._ui.label_layer_input,
                self._ui.input_layer_number,
                self._ui.label_image_number,
                self._ui.input_image_number,
                self._ui.label_image_count,
                self._ui.button_show_grid_line_structure,
                self._ui.checkbox_show_grid,
                self._ui.button_interface_enabled,
                self._ui.label_work_with_layers,
                self._ui.slider_work_with_grid_or_layer,
                self._ui.label_work_with_grid,
                self._ui.button_zoom_in,
                self._ui.button_zoom_out,
                self._ui.button_zoom_reset,
            ]
            
            for widget in toolbar_widgets:
                widget.setParent(None)
                toolbar_layout.addWidget(widget)
            
            self._ui.input_layer_number.setMaximumSize(71, 31)
            self._ui.input_image_number.setMaximumSize(71, 31)
            self._ui.slider_work_with_grid_or_layer.setMaximumSize(81, 31)
            self._ui.button_zoom_reset.setMaximumSize(41, 31)
            
            toolbar_layout.addStretch()
            toolbar_container.setFixedHeight(35)
            
            central_layout.addWidget(toolbar_container)
            
            self._ui.TabWidget.setParent(None)
            self._ui.TabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            central_layout.addWidget(self._ui.TabWidget)
        
        if self._ui.MainScreen.layout() is None:
            layout = QHBoxLayout(self._ui.MainScreen)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(20)
            
            self._ui.image1.setParent(None)
            self._ui.image1.setScaledContents(False)
            self._ui.image1.setAlignment(Qt.AlignCenter)
            self._ui.image1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._ui.image1.setMinimumSize(100, 100)
            layout.addWidget(self._ui.image1, 1)
            
            self._ui.image2.setParent(None)
            self._ui.image2.setScaledContents(False)
            self._ui.image2.setAlignment(Qt.AlignCenter)
            self._ui.image2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._ui.image2.setMinimumSize(100, 100)
            layout.addWidget(self._ui.image2, 1)

    def _init_ui_connections(self):
        self._connect_sliders()
        self._connect_buttons()
        self._connect_actions()
        self._connect_inputs()
        self._connect_checkboxes()
        self._ui.image2.installEventFilter(self)
    
    def _connect_sliders(self):
        self._ui.slider_tilt.valueChanged.connect(self._on_tilt_slider_changed)
        self._ui.slider_grid_size.valueChanged.connect(self._on_grid_size_slider_changed)
        
        if hasattr(self._ui, 'slider_work_with_grid_or_layer'):
            self._ui.slider_work_with_grid_or_layer.setMinimum(0)
            self._ui.slider_work_with_grid_or_layer.setMaximum(99)
            self._ui.slider_work_with_grid_or_layer.setValue(0)
            self._ui.slider_work_with_grid_or_layer.valueChanged.connect(self._on_grid_layer_slider_changed)
    
    def _connect_buttons(self):
        self._ui.button_select_excel_file.clicked.connect(self.browse_excel_file)
        self._ui.button_interface_enabled.clicked.connect(self._main_controller.on_reverse_ui_toggled)
        
        self._ui.button_create_grid.clicked.connect(self._main_controller.create_grid_for_current_image)
        self._ui.button_delete_grid.clicked.connect(self._main_controller.delete_grid_for_current_image)
        
        self._ui.button_grid_copy.clicked.connect(self._main_controller.copy_grid_to_all_next)
        self._ui.button_grid_delete_all.clicked.connect(self._main_controller.delete_all_grids)
        self._ui.button_grid_copy_2.clicked.connect(self._main_controller.copy_grid_from_previous)
        
        if hasattr(self._ui, 'button_reset_buttons'):
            self._ui.button_reset_buttons.clicked.connect(self.on_reset_hotkeys_to_default)
        
        self._ui.button_zoom_in.clicked.connect(self._zoom_in)
        self._ui.button_zoom_out.clicked.connect(self._zoom_out)
        self._ui.button_zoom_reset.clicked.connect(self._zoom_reset)
    
    def _connect_actions(self):
        # меню проекта
        self._ui.action_project_menu_crop.triggered.connect(self.open_folder_to_crop)
        self._ui.action_project_menu_save.triggered.connect(self._main_controller.save_project)
        self._ui.action_project_menu_open_another_project.triggered.connect(self.on_project_open)
        self._ui.action_project_menu_open_start_window.triggered.connect(
            lambda: self.on_project_close(do_open_start_window=True))
        self._ui.action_project_menu_save_excel.triggered.connect(self._main_controller.save_to_excel)
        self._ui.action_open_overview.triggered.connect(self._open_user_overview)
        
        if hasattr(self._ui, 'action_project_autosave_enabled'):
            self._ui.action_project_autosave_enabled.setCheckable(True)
            self._ui.action_project_autosave_enabled.triggered.connect(self._on_autosave_toggled)
        
        # навигация вперед назад по линиям роста и изображениям
        self._ui.action_next_layer.triggered.connect(self._on_next_layer_or_grid)
        self._ui.action_previous_layer.triggered.connect(self._on_previous_layer_or_grid)
        self._ui.action_next_image.triggered.connect(self._main_controller.go_next_image)
        self._ui.action_previous_image.triggered.connect(self._main_controller.go_previous_image)
        
        # удалить слой или точки
        self._ui.action_delete_all_points.triggered.connect(self._confirm_delete_all_points_on_image)
        self._ui.action_delete_all_points_everywhere.triggered.connect(self._confirm_delete_all_points_everywhere)
        self._ui.action_delete_layer.triggered.connect(self._on_delete_layer_or_grid)
        self._ui.action_delete_layer_points.triggered.connect(self._on_delete_points_layer_or_grid)
        
        # генерация
        self._ui.action_generate_on_image.triggered.connect(self._main_controller.generate_intersections_for_current_image)
        self._ui.action_generate_on_layer.triggered.connect(self._main_controller.generate_intersections_for_current_layer)
        self._ui.action_generate_all.triggered.connect(self._main_controller.generate_intersections_for_all_images)
        
        mode_actions = [
            (self._ui.action_select_center, InteractionMode.SELECT_CENTER.value),
            (self._ui.action_add_layer_point, InteractionMode.ADD_POINT.value),
            (self._ui.action_move_layer_point, InteractionMode.MOVE_POINT.value),
            (self._ui.action_delete_layer_point, InteractionMode.DELETE_POINT.value),
        ]
        
        self._mode_action_group = QActionGroup(self)
        self._mode_action_group.setExclusive(True)
        
        for action, mode in mode_actions:
            action.setCheckable(True)
            self._mode_action_group.addAction(action)
            action.triggered.connect(lambda checked=False, m=mode: self._on_mode_action_triggered(m))
        
        self._ui.action_select_center.setChecked(True)
        
        if hasattr(self._ui, 'action_open_about_window'):
            self._ui.action_open_about_window.triggered.connect(self.on_open_github_link)
    
    def _on_mode_action_triggered(self, mode):
        self._main_controller.set_mode(mode)
    
    @pyqtSlot(int)
    def _handle_mode_changed(self, mode):
        mode_map = {
            InteractionMode.SELECT_CENTER.value: self._ui.action_select_center,
            InteractionMode.ADD_POINT.value: self._ui.action_add_layer_point,
            InteractionMode.MOVE_POINT.value: self._ui.action_move_layer_point,
            InteractionMode.DELETE_POINT.value: self._ui.action_delete_layer_point,
        }
        
        action = mode_map.get(mode)
        if action and not action.isChecked():
            action.setChecked(True)
    
    def _connect_inputs(self):
        input_connections = [
            (self._ui.input_save_file_path, lambda text: self._model.update_attribute('excel_file', text)),
            (self._ui.input_tilt, self._update_tilt),
            (self._ui.input_division_count, self._update_division_count),
            (self._ui.input_image_scale_nm, self._update_nm_value),
            (self._ui.input_sheet_name, lambda text: self._model.update_attribute('sheet_name', text)),
            (self._ui.input_grid_size_multiplier, self._update_grid_scale),
            (self._ui.input_ellipsoid_height, self._update_ellipse_width),
            (self._ui.input_ellipsoid_width, self._update_ellipse_height),
        ]

        if hasattr(self._ui, 'input_accuracy'):
            input_connections.append((self._ui.input_accuracy, self._update_accuracy))
        
        for widget, callback in input_connections:
            widget.textChanged.connect(callback)
        
        return_press_widgets = [
            self._ui.input_save_file_path,
            self._ui.input_tilt,
            self._ui.input_division_count,
            self._ui.input_image_scale_nm,
            self._ui.input_sheet_name,
            self._ui.input_grid_size_multiplier,
            self._ui.input_ellipsoid_height,
            self._ui.input_ellipsoid_width,
            self._ui.input_layer_number,
            self._ui.input_image_number,
        ]

        if hasattr(self._ui, 'input_accuracy'):
            return_press_widgets.append(self._ui.input_accuracy)
        
        for widget in return_press_widgets:
            widget.returnPressed.connect(lambda w=widget: w.clearFocus())
        
        self._ui.input_layer_number.returnPressed.connect(self.on_input_layer_number)
        self._ui.input_image_number.returnPressed.connect(self.on_input_image_number)
    
    def _connect_checkboxes(self):
        self._ui.checkbox_show_grid.stateChanged.connect(
            lambda state: self._model.update_attribute('show_grid', not self._model.show_grid)
        )
        self._ui.checkbox_half_grid_invisible.stateChanged.connect(
            lambda state: self._model.update_attribute('half_grid', not self._model.half_grid)
        )
        self._ui.checkbox_save_by_half.stateChanged.connect(
            lambda state: self._model.update_attribute('save_half', not self._model.save_half)
        )
        self._ui.checkbox_interpolation_enabled.stateChanged.connect(
            lambda state: self._model.update_attribute('interpolation_enabled', bool(state))
        )

        self._ui.checkbox_ask_new_image_copy.stateChanged.connect(
            lambda state: self._model.update_attribute('checkbox_ask_new_image_copy', bool(state))
        )
        self._ui.checkbox_copy_grid.stateChanged.connect(
            lambda state: self._model.update_attribute('checkbox_copy_grid', bool(state))
        )
        self._ui.checkbox_copy_layers.stateChanged.connect(
            lambda state: self._model.update_attribute('checkbox_copy_layers', bool(state))
        )
        
        self._ui.grid_radial_checkbox.toggled.connect(
            lambda: self.on_grid_type_changed(GridType.RADIAL.value)
        )
        self._ui.grid_vertical_checkbox.toggled.connect(
            lambda: self.on_grid_type_changed(GridType.VERTICAL.value)
        )
        self._ui.grid_horizontal_checkbox.toggled.connect(
            lambda: self.on_grid_type_changed(GridType.HORIZONTAL.value)
        )
        self._ui.grid_elipsoid_checkbox.toggled.connect(
            lambda: self.on_grid_type_changed(GridType.ELLIPSOID.value)
        )
    
    def _init_model_connections(self):
        # Set initial values from model
        self._sync_ui_with_model()
        
        # Listen to model changes
        self._model.attributeChanged.connect(self.on_variables_changed)
        self._model.attributeChanged.connect(self.draw_ui_images)
        
        # Connect controller signals
        self._main_controller.update_ui.connect(self.draw_ui_images)
        self._main_controller.modeChanged.connect(self._handle_mode_changed)
        if hasattr(self._main_controller, "update_image2"):
            self._main_controller.update_image2.connect(lambda: self.draw_image(2))
    
    def _sync_ui_with_model(self):
        self._ui.input_image_number.setText(str(self._model.current_image + 1))
        self._ui.input_layer_number.setText(str(self._model.current_layer + 1))
        self._ui.input_save_file_path.setText(str(self._model.excel_file))
        self._ui.input_sheet_name.setText(str(self._model.sheet_name))
        self._ui.input_tilt.setText(str(self._model.tilt))
        self._ui.input_division_count.setText(str(self._model.division_count))
        self._ui.input_image_scale_nm.setText(str(self._model.nm_value))
        self._ui.input_grid_size_multiplier.setText(str(self._model.grid_scale))
        self._ui.input_ellipsoid_height.setText(str(self._model.ellipse_width))
        self._ui.input_ellipsoid_width.setText(str(self._model.ellipse_height))
        #self._ui.input_center_x.setText(str(self._model.center_x))
        #self._ui.input_center_y.setText(str(self._model.center_y))
        
        if hasattr(self._ui, 'input_accuracy'):
            self._ui.input_accuracy.setText(str(self._model.excel_save_accuracy))

        if hasattr(self._ui, 'label_image_count'):
            self._ui.label_image_count.setText(f"из {len(self._model.crystal_object)}")

        self._ui.slider_tilt.setValue(self._model.tilt)
        slider_grid_value = int(((self._model.grid_scale - 0.1) / 9.9) * 100)
        self._ui.slider_grid_size.setValue(slider_grid_value)
        
        self._ui.grid_radial_checkbox.setChecked(self._model.grid_type == GridType.RADIAL.value)
        self._ui.grid_vertical_checkbox.setChecked(self._model.grid_type == GridType.VERTICAL.value)
        self._ui.grid_horizontal_checkbox.setChecked(self._model.grid_type == GridType.HORIZONTAL.value)
        self._ui.grid_elipsoid_checkbox.setChecked(self._model.grid_type == GridType.ELLIPSOID.value)
        
        if hasattr(self._ui, 'slider_work_with_grid_or_layer'):
            target_slider_value = 99 if self._model.work_with_grid_mode else 0
            old_state = self._ui.slider_work_with_grid_or_layer.blockSignals(True)
            self._ui.slider_work_with_grid_or_layer.setValue(target_slider_value)
            self._ui.slider_work_with_grid_or_layer.blockSignals(old_state)

        self._ui.checkbox_half_grid_invisible.setChecked(self._model.half_grid)
        self._ui.checkbox_show_grid.setChecked(self._model.show_grid)
        self._ui.checkbox_save_by_half.setChecked(self._model.save_half)
        self._ui.checkbox_interpolation_enabled.setChecked(self._model.interpolation_enabled)
        self._ui.checkbox_ask_new_image_copy.setChecked(self._model.checkbox_ask_new_image_copy)
        self._ui.checkbox_copy_grid.setChecked(self._model.checkbox_copy_grid)
        self._ui.checkbox_copy_layers.setChecked(self._model.checkbox_copy_layers)
        
        if hasattr(self._ui, 'action_project_autosave_enabled'):
            self._ui.action_project_autosave_enabled.setChecked(self._model.autosave)
            if self._model.autosave:
                self._autosave_timer.start()
            else:
                self._autosave_timer.stop()
    
    def _init_shortcuts(self):
        # стандартные хоткеи
        self._undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self._undo_shortcut.activated.connect(self._main_controller.undo)
        
        self._redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self._redo_shortcut.activated.connect(self._main_controller.redo)
        
        self._escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self._escape_shortcut.activated.connect(self._clear_focus_on_escape)
        
        self.setup_hotkeys()
    
    def _init_autosave_timer(self):
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._on_autosave_timer)
        self._autosave_timer.setInterval(5 * 60 * 1000)  # 5 min

    def _update_window_title(self):
        if hasattr(self._model, 'settings_file') and self._model.settings_file:
            project_name = os.path.splitext(os.path.basename(self._model.settings_file))[0]
            self.setWindowTitle(f"CrystalGrowthTool - {project_name}")
        else:
            self.setWindowTitle("CrystalGrowthTool")

    def _init_slider_sync(self):
        self._ui.slider_tilt.valueChanged.connect(self._on_tilt_slider_changed)
        self._ui.slider_grid_size.valueChanged.connect(self._on_grid_size_slider_changed)
        self._ui.input_tilt.textChanged.connect(self._on_tilt_input_changed)
        self._ui.input_grid_size_multiplier.textChanged.connect(self._on_grid_size_input_changed)
        
        self._ui.slider_tilt.setValue(self._model.tilt)
        slider_grid_value = int(((self._model.grid_scale - 0.1) / 9.9) * 100)
        self._ui.slider_grid_size.setValue(slider_grid_value)
    
    def setup_hotkeys(self):
        hotkey_mappings = {
            'saveProject': (self._ui.key_save_project, self._main_controller.save_project),
            'closeProject': (self._ui.key_close_project, self.on_project_close),
            'cropImages': (self._ui.key_crop_images, self.open_folder_to_crop),
            'saveExcel': (self._ui.key_save_excel, lambda: self._main_controller.save_to_excel()),
            'switchInterfaceMode': (self._ui.key_switch_interface_mode, self._main_controller.on_reverse_ui_toggled),
            'previousImage': (self._ui.key_previous_image, self._main_controller.go_previous_image),
            'nextImage': (self._ui.key_next_image, self._main_controller.go_next_image),
            'selectCenter': (self._ui.key_select_center, lambda: self._main_controller.set_mode(InteractionMode.SELECT_CENTER.value)),
            'generateOnLayer': (self._ui.key_generate_on_layer, self._main_controller.generate_intersections_for_current_layer),
            'generateOnImage': (self._ui.key_generate_on_image, self._main_controller.generate_intersections_for_current_image),
            'generateAll': (self._ui.key_generate_all, self._main_controller.generate_intersections_for_all_images),
            'addLayerPoint': (self._ui.key_add_layer_point, lambda: self._main_controller.set_mode(InteractionMode.ADD_POINT.value)),
            'moveLayerPoint': (self._ui.key_move_layer_point, lambda: self._main_controller.set_mode(InteractionMode.MOVE_POINT.value)),
            'deleteLayerPoint': (self._ui.key_delete_layer_point, lambda: self._main_controller.set_mode(InteractionMode.DELETE_POINT.value)),
            'deleteLayer': (self._ui.key_delete_layer, self._main_controller.delete_layer),
            'deleteLayerPoints': (self._ui.key_delete_layer_points, self._confirm_delete_layer_points),
            'deleteAllPoints': (self._ui.key_delete_all_points, self._confirm_delete_all_points_on_image),
            'nextLayer': (self._ui.key_next_layer, self._main_controller.go_next_layer),
            'previousLayer': (self._ui.key_previous_layer, self._main_controller.go_previous_layer),
            'zoomIn': (self._ui.key_zoom_in, self._zoom_in),
            'zoomOut': (self._ui.key_zoom_out, self._zoom_out),
        }

        self.hotkey_controller.setup_hotkeys(hotkey_mappings)
    
    def on_reset_hotkeys_to_default(self):
        self.hotkey_manager.hotkeys = self.hotkey_manager.default_hotkeys.copy()
        self.hotkey_manager.save_hotkeys()
        self.hotkey_controller.refresh_shortcuts()
    
    def closeEvent(self, event):
        if self._autosave_timer:
            self._autosave_timer.stop()

        close_ok = True
        
        if not self._force_close:
            if self.layers_window or self.images_window or self.grid_window:
                close_ok = self.on_project_close(do_open_start_window=False)

        if not close_ok:
            event.ignore()
            return

        if hasattr(self, 'layers_window'):
            self.layers_window.setParent(None)
            self.layers_window.deleteLater()
            self.layers_window = None

        if hasattr(self, 'images_window'):
            self.images_window.setParent(None)
            self.images_window.deleteLater()
            self.images_window = None

        if hasattr(self, 'grid_window'):
            self.grid_window.setParent(None)
            self.grid_window.deleteLater()
            self.grid_window = None

        super().closeEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_model') and self._model:
            self.draw_ui_images()
    
    def on_input_layer_number(self):
        value = self.validate_int_input(
            self._ui.input_layer_number, 1, 999999, 
            "Номер линии" if self._model.work_with_grid_mode else "Номер слоя", 
            "_last_valid_layer_number" 
        )
        self._ui.input_layer_number.setText(str(value))
        
        if self._model.work_with_grid_mode:
            self._main_controller.go_to_grid_line(value - 1)
        else:
            self._main_controller.go_to_layer(value - 1)

    def on_input_image_number(self):
        value = self.validate_int_input(
            self._ui.input_image_number, 1, 999999, "Номер снимка", "_last_valid_image_number"
        )
        self._ui.input_image_number.setText(str(value))
        self._main_controller.go_to_image(value - 1)

    def _clear_focus_on_escape(self):
        focused_widget = QApplication.focusWidget()
        if focused_widget:
            focused_widget.clearFocus()

    def localize_ui(self):
        def set_keysequence_placeholders(widgets, placeholder="введите комбинацию"):
            for widget in widgets:
                line_edit = widget.findChild(QLineEdit, "qt_keysequenceedit_lineedit")
                if line_edit:
                    line_edit.setPlaceholderText(placeholder)

        keysequence_widgets = [
            self._ui.key_save_project,
            #self._ui.key_open_project,
            self._ui.key_close_project,
            self._ui.key_crop_images,
            self._ui.key_save_excel,
            self._ui.key_switch_interface_mode,
            self._ui.key_previous_image,
            self._ui.key_next_image,
            self._ui.key_select_center,
            self._ui.key_generate_on_image,
            self._ui.key_generate_all,
            self._ui.key_generate_on_layer,
            self._ui.key_add_layer_point,
            self._ui.key_move_layer_point,
            self._ui.key_delete_layer_point,
            self._ui.key_delete_layer,
            self._ui.key_delete_all_points,
            self._ui.key_delete_layer_points,
            self._ui.key_next_layer,
            self._ui.key_previous_layer,
        ]
        set_keysequence_placeholders(keysequence_widgets)


    def on_variables_changed(self, name, value):
        if name == 'interpolation_enabled':
             if self._ui.checkbox_interpolation_enabled.isChecked() != value:
                 self._ui.checkbox_interpolation_enabled.setChecked(value)
        
        elif name == 'show_grid':
             if self._ui.checkbox_show_grid.isChecked() != value:
                 self._ui.checkbox_show_grid.setChecked(value)

        elif name == 'half_grid':
             if self._ui.checkbox_half_grid_invisible.isChecked() != value:
                 self._ui.checkbox_half_grid_invisible.setChecked(value)
        
        elif name == 'save_half':
             if self._ui.checkbox_save_by_half.isChecked() != value:
                 self._ui.checkbox_save_by_half.setChecked(value)
                 
        elif name == 'checkbox_ask_new_image_copy':
             if self._ui.checkbox_ask_new_image_copy.isChecked() != value:
                 self._ui.checkbox_ask_new_image_copy.setChecked(value)

        elif name == 'checkbox_copy_grid':
             if self._ui.checkbox_copy_grid.isChecked() != value:
                 self._ui.checkbox_copy_grid.setChecked(value)
                 
        elif name == 'checkbox_copy_layers':
             if self._ui.checkbox_copy_layers.isChecked() != value:
                 self._ui.checkbox_copy_layers.setChecked(value)

        elif name == 'current_image':
             self._ui.input_image_number.setText(str(value + 1))
             
        elif name == 'excel_save_accuracy' and hasattr(self._ui, 'input_accuracy'):
             self._ui.input_accuracy.setText(str(value))

        elif name == 'current_layer':
             if not self._model.work_with_grid_mode:
                self._ui.input_layer_number.setText(str(value + 1))
        
        elif name == 'current_grid_line':
             if self._model.work_with_grid_mode:
                self._ui.input_layer_number.setText(str(value + 1))
                
        elif name == 'work_with_grid_mode':
            if value:
                self._ui.input_layer_number.setText(str(self._model.current_grid_line + 1))
            else:
                self._ui.input_layer_number.setText(str(self._model.current_layer + 1))
        
        elif name == 'grid_type':
            self._ui.grid_radial_checkbox.setChecked(value == GridType.RADIAL.value)
            self._ui.grid_vertical_checkbox.setChecked(value == GridType.VERTICAL.value)
            self._ui.grid_horizontal_checkbox.setChecked(value == GridType.HORIZONTAL.value)
            self._ui.grid_elipsoid_checkbox.setChecked(value == GridType.ELLIPSOID.value)

    def on_grid_type_changed(self, new_grid_type):
        if new_grid_type == self._model.grid_type:
            return

        self._ui.grid_radial_checkbox.setChecked(new_grid_type == GridType.RADIAL.value)
        self._ui.grid_vertical_checkbox.setChecked(new_grid_type == GridType.VERTICAL.value)
        self._ui.grid_horizontal_checkbox.setChecked(new_grid_type == GridType.HORIZONTAL.value)
        self._ui.grid_elipsoid_checkbox.setChecked(new_grid_type == GridType.ELLIPSOID.value)
        self._model.update_attribute('grid_type', int(new_grid_type))

    @staticmethod
    def _resource_path(filename):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, "resources", filename)

    def _open_user_overview(self):
        try:
            file_path = self._resource_path("userdoc.pdf")
            if os.path.exists(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            else:
                QMessageBox.warning(self, "Ошибка", f"Файл документации не найден:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть документацию: {e}")

    def open_folder_to_crop(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self._main_controller.crop_images(folder)

    def browse_excel_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть файл', '', "Excel(*.xlsx *.xls)")
        if fname[0]:
            self._ui.input_save_file_path.setText(fname[0])

    def on_open_github_link(self):
        QDesktopServices.openUrl(QUrl('https://github.com/justwolk/CrystalGrowthTool/'))

    def _on_autosave_timer(self):
        if self._model and self._model.autosave:
            self._main_controller.save_project()
    
    def _on_autosave_toggled(self):
        is_checked = self._ui.action_project_autosave_enabled.isChecked()
        self._model.update_attribute('autosave', is_checked)
        
        if is_checked:
            self._autosave_timer.start()
        else:
            self._autosave_timer.stop()
        
    def on_project_close(self, do_open_start_window=False):
        messageBox = QMessageBox(self)
        messageBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        messageBox.button(QMessageBox.StandardButton.Yes).setText("Да")
        messageBox.button(QMessageBox.StandardButton.No).setText("Нет")
        messageBox.button(QMessageBox.StandardButton.Cancel).setText("Отмена")
        messageBox.setWindowTitle("Закрыть программу")
        messageBox.setText("Сохранить ли проект перед закрытием?")
        messageBox.setDefaultButton(QMessageBox.StandardButton.Yes)

        messageBox.exec()
        clicked_button = messageBox.clickedButton()

        if clicked_button == messageBox.button(QMessageBox.StandardButton.Yes):
            self._main_controller.save_project()
            self._force_close = True
            if do_open_start_window:
                self.projectClosed.emit()
            return True
        elif clicked_button == messageBox.button(QMessageBox.StandardButton.No):
            self._force_close = True
            if do_open_start_window:
                self.projectClosed.emit()
            return True
        else:
            return False

    def on_project_open(self):
        from PySide2.QtWidgets import QFileDialog
        file, _ = QFileDialog.getOpenFileName(self, "Открыть проект", '', 'Crystal Project Files (*.crystal)')
        if file:
            self.projectOpenRequested.emit(file)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Alt and not event.isAutoRepeat():
            self._main_controller.set_alt_mode(True)
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Alt and not event.isAutoRepeat():
            self._main_controller.set_alt_mode(False)
        super().keyReleaseEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self._clear_focus_on_escape()
            return True
        
        if obj == self._ui.image2:
            if self._handle_image2_wheel_event(event):
                return True
            if self._handle_image2_pan_events(event):
                return True
            if self._handle_image2_mouse_events(event):
                return True
        
        if (self._ui.TabWidget.currentWidget().objectName() == "Hotkeys" and 
            event.type() == QEvent.MouseButtonPress):
            return self._handle_hotkey_focus_clear(event)
        
        return super().eventFilter(obj, event)
    
    def _handle_image2_wheel_event(self, event):
        if event.type() != QEvent.Wheel:
            return False
        
        if self._image2_handler.zoom(
            event.angleDelta().y(), 
            event.pos(),
            self._ui.image2.width(),
            self._ui.image2.height()
        ):
            self.draw_ui_images()
        return True
    
    def _handle_image2_pan_events(self, event):
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.MiddleButton:
            if self._image2_handler.start_pan(event.pos()):
                self._ui.image2.setCursor(Qt.ClosedHandCursor)
            return True
        
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.MiddleButton:
            self._image2_handler.reset_pan()
            self._ui.image2.setCursor(Qt.ArrowCursor)
            return True
        
        if event.type() == QEvent.MouseMove and self._image2_handler.update_pan(event.pos()):
            self.draw_image(2)
            return True
        
        return False
    
    def _handle_image2_mouse_events(self, event):
        if event.type() not in (QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease):
            return False
        
        if hasattr(event, 'button') and event.button() == Qt.MiddleButton:
            return True
        if self._image2_handler.panning and event.type() == QEvent.MouseMove:
            return True
        
        pixmap_size = getattr(self._image2_handler, 'pixmap_size', None)
        label_size = getattr(self._image2_handler, 'label_size', None)
        
        if not pixmap_size or not label_size:
            if self._ui.image2.pixmap():
                pixmap_size = self._ui.image2.pixmap().size()
                label_size = self._ui.image2.size()
            else:
                return False
        
        alt_state = self._main_controller.get_alt_mode_state()
        if alt_state['active'] and event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self._main_controller.handle_alt_mode_click(
                event.pos(), pixmap_size, label_size,
                self._image2_handler.scale,
                self._image2_handler.base_scale,
                self._image2_handler.offset
            )
            return True
        
        if event.type() == QEvent.MouseButtonPress:
            self._main_controller.handle_mouse_click(
                event, pixmap_size, label_size,
                self._image2_handler.scale,
                self._image2_handler.base_scale,
                self._image2_handler.offset
            )
        
        event_type = {
            QEvent.MouseButtonPress: 'press',
            QEvent.MouseMove: 'move',
            QEvent.MouseButtonRelease: 'release'
        }[event.type()]
        
        self._main_controller.handle_drag_and_drop(
            event_type, event, pixmap_size, label_size,
            self._image2_handler.scale,
            self._image2_handler.base_scale,
            self._image2_handler.offset
        )
        return True
    
    def _handle_hotkey_focus_clear(self, event):
        focus_widget = QApplication.focusWidget()
        if isinstance(focus_widget, (QLineEdit, QKeySequenceEdit)):
            clicked_widget = self.childAt(event.pos())
            if clicked_widget is None or clicked_widget != focus_widget:
                focus_widget.clearFocus()
        return False

    def validate_int_input(self, widget, min_value=1, max_value=999999, field_name="", last_valid_attr=None):
        text = widget.text()
        if not re.fullmatch(r"\d{1,6}", text):
            QMessageBox.critical(
                self, "Ошибка", 
                f"{field_name} должно быть числом от {min_value} до {max_value}"
            )
            return getattr(self, last_valid_attr, min_value)
        
        value = int(text)
        if not (min_value <= value <= max_value):
            QMessageBox.critical(
                self, "Ошибка", 
                f"{field_name} должно быть числом от {min_value} до {max_value}"
            )
            return getattr(self, last_valid_attr, min_value)
        
        if last_valid_attr:
            setattr(self, last_valid_attr, value)
        return value

    def _update_tilt(self):
        try:
            text = self._ui.input_tilt.text().strip()
            if text and text not in ('-', '+'):
                value = max(-90, min(90, int(text)))
                self._model.update_attribute('tilt', value)
        except ValueError:
            pass
    
    def _update_division_count(self):
        try:
            text = self._ui.input_division_count.text().strip()
            if text:
                value = max(1, int(text))
                self._model.update_attribute('division_count', value)
        except ValueError:
            pass
    
    def _update_nm_value(self):
        try:
            text = self._ui.input_image_scale_nm.text().strip()
            if text:
                value = max(1, int(text))
                self._model.update_attribute('nm_value', value)
        except ValueError:
            pass
    
    def _update_grid_scale(self):
        try:
            text = self._ui.input_grid_size_multiplier.text().strip()
            if text:
                value = max(0.1, min(10.0, float(text)))
                self._model.update_attribute('grid_scale', value)
        except ValueError:
            pass
    
    def _update_ellipse_width(self):
        try:
            text = self._ui.input_ellipsoid_height.text().strip()
            if text:
                value = max(1, int(text))
                self._model.update_attribute('ellipse_width', value)
        except ValueError:
            pass
    
    def _update_ellipse_height(self):
        try:
            text = self._ui.input_ellipsoid_width.text().strip()
            if text:
                value = max(1, int(text))
                self._model.update_attribute('ellipse_height', value)
        except ValueError:
            pass

    def _update_accuracy(self):
        try:
            text = self._ui.input_accuracy.text().strip()
            if text:
                value = max(0, min(6, int(text)))
                self._model.update_attribute('excel_save_accuracy', value)
        except ValueError:
            pass

    def _on_tilt_slider_changed(self, value):
        self._ui.input_tilt.setText(str(value))

    def _on_grid_size_slider_changed(self, value):
        decimal_value = 0.1 + (value / 100.0) * 9.9
        self._ui.input_grid_size_multiplier.setText(f"{decimal_value:.1f}")
        self._model.update_attribute('grid_scale', decimal_value)

    def _on_tilt_input_changed(self, text):
        try:
            value = int(text)
            self._ui.slider_tilt.setValue(value)
        except ValueError:
            pass

    def _on_grid_size_input_changed(self, text):
        try:
            value = float(text)
            value = max(0.1, min(10.0, value))
            slider_value = int(((value - 0.1) / 9.9) * 100)
            
            old_state = self._ui.slider_grid_size.blockSignals(True)
            self._ui.slider_grid_size.setValue(slider_value)
            self._ui.slider_grid_size.blockSignals(old_state)
            
            self._model.update_attribute('grid_scale', value)
        except ValueError:
            pass
    
    def _on_grid_layer_slider_changed(self, value):
        if value < 50:
            self._ui.slider_work_with_grid_or_layer.setValue(0)
            self._model.update_attribute('work_with_grid_mode', False)
        else:
            self._ui.slider_work_with_grid_or_layer.setValue(99)
            self._model.update_attribute('work_with_grid_mode', True)
    
    def _on_next_layer_or_grid(self):
        if self._model.work_with_grid_mode:
            self._main_controller.go_next_grid_line()
        else:
            self._main_controller.go_next_layer()
    
    def _on_previous_layer_or_grid(self):
        if self._model.work_with_grid_mode:
            self._main_controller.go_previous_grid_line()
        else:
            self._main_controller.go_previous_layer()
    
    def _on_delete_layer_or_grid(self):
        if self._model.work_with_grid_mode:
            current_line = self._model.current_grid_line
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Подтверждение удаления")
            msg_box.setText(f"Удалить линию сетки {current_line + 1}?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.button(QMessageBox.Yes).setText("Да")
            msg_box.button(QMessageBox.No).setText("Нет")
            msg_box.setDefaultButton(QMessageBox.No)
            
            if msg_box.exec_() == QMessageBox.Yes:
                crystal_object = self._model.crystal_object[self._model.current_image]
                if current_line < len(crystal_object.grid_lines):
                    del crystal_object.grid_lines[current_line]
                    if self._model.current_grid_line >= len(crystal_object.grid_lines):
                        self._model.update_attribute('current_grid_line', max(0, len(crystal_object.grid_lines) - 1))
                self._main_controller.update_ui.emit()
        else:
            self._main_controller.delete_layer()
    
    def _on_delete_points_layer_or_grid(self):
        if self._model.work_with_grid_mode:
            current_line = self._model.current_grid_line
            crystal_object = self._model.crystal_object[self._model.current_image]
            
            if current_line >= len(crystal_object.grid_lines):
                return
            
            point_count = len(crystal_object.grid_lines[current_line])
            
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Подтверждение удаления")
            msg_box.setText(f"Удалить все {point_count} точек на линии {current_line + 1}?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.button(QMessageBox.Yes).setText("Да")
            msg_box.button(QMessageBox.No).setText("Нет")
            msg_box.setDefaultButton(QMessageBox.No)
            
            if msg_box.exec_() == QMessageBox.Yes:
                crystal_object.grid_lines[current_line] = []
                self._main_controller.update_ui.emit()
        else:
            self._confirm_delete_layer_points()

    def _confirm_delete_layer_points(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Удалить все точки на текущей ступени?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Да")
        msg_box.button(QMessageBox.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self._main_controller.delete_layer_points()
    
    def _confirm_delete_all_points_on_image(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Удалить все координаты на текущем снимке?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.StandardButton.Yes).setText("Да")
        msg_box.button(QMessageBox.StandardButton.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self._main_controller.clear_all_points_on_image()
    
    def _confirm_delete_all_points_everywhere(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Удалить все координаты на всех снимках?")
        msg_box.setInformativeText("Это действие нельзя отменить!")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.StandardButton.Yes).setText("Да")
        msg_box.button(QMessageBox.StandardButton.No).setText("Нет")
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self._main_controller.clear_all_points_everywhere()

    def _zoom_in(self):
        label_center = QPoint(self._ui.image2.width() // 2, self._ui.image2.height() // 2)
        if self._image2_handler.zoom(120, label_center, self._ui.image2.width(), self._ui.image2.height()):
            self.draw_ui_images()
    
    def _zoom_out(self):
        label_center = QPoint(self._ui.image2.width() // 2, self._ui.image2.height() // 2)
        if self._image2_handler.zoom(-120, label_center, self._ui.image2.width(), self._ui.image2.height()):
            self.draw_ui_images()
    
    def _zoom_reset(self):
        self._image2_handler.scale = 1.0
        self._image2_handler.offset = QPoint(0, 0)
        self.draw_ui_images()
