import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Signal as pyqtSignal, Slot as pyqtSlot
from PySide6.QtCore import QPoint, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QPixmap, QPainter, QPen, Qt, QPainterPath, QFont, \
    QColor, QIntValidator

from View.ui_main import Ui_MainWindow
from Modules.calculate_grid import fill_grid_lines
from Modules.intrpolate_line import cubic_spline_interpolation


class MainView(QMainWindow):
    def __init__(self, model, main_controller):
        super().__init__()

        self._model = model
        self._main_controller = main_controller
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        #режимы клика на рабочее (правое) изображение
        MODE_SELECT_CENTER = 1
        MODE_ADD_GROW_LINE_POINT = 3
        MODE_MOVE_GROW_LINE_POINT = 4
        MODE_DELETE_GROW_LINE_POINT = 5
        MODE_SELECT_DOTS = 7
        MODE_SELECT_GROW_LINE_LAYER = 8
        MODE_DELETE_GROW_LINE_LAYER = 9

        # устанавливаем сигналы на элементы управления программы
        self._ui.buttonResetCenter.clicked.connect(lambda: self._main_controller.reset_center_position)
        self._ui.buttonApplyCenter.clicked.connect(lambda: self._main_controller.apply_center_position(int(self._ui.inputCenterX.text()), int(self._ui.inputCenterY.text())))
        self._ui.buttonSelectFile.clicked.connect(self.browse_excel_file)
        self._ui.buttonSaveSettings.clicked.connect(self.save_settings)

        self._ui.actionCropImage.triggered.connect(self.open_folder_to_crop)
        self._ui.actionOpenImages.triggered.connect(self.open_image_folder)
        self._ui.actionSave.triggered.connect(lambda: self._main_controller.save_to_exсel(self._ui.image2.pixmap()))
        self._ui.actionReverseInterface.triggered.connect(self._main_controller.on_reverse_ui_toggled)
        self._ui.actionNextLayer.triggered.connect(self._main_controller.go_next_image)
        self._ui.actionPreviousLayer.triggered.connect(self._main_controller.go_previous_image)
        self._ui.actionGeneratePoints.triggered.connect(self._main_controller.generate_points_layer)
        self._ui.actionGenerateAll.triggered.connect(self._main_controller.generate_points_image)

        # сигналы на кнопки взаимодействия с правым (рабочим) изображением, изменить режим работы с изображением
        self._ui.actionSelectCenter.triggered.connect(lambda: self._main_controller.set_mode(MODE_SELECT_CENTER))
        self._ui.actionAddGrowLinePoint.triggered.connect(lambda: self._main_controller.set_mode(MODE_ADD_GROW_LINE_POINT))
        self._ui.actionMoveGrowLinePoint.triggered.connect(lambda: self._main_controller.set_mode(MODE_MOVE_GROW_LINE_POINT))
        self._ui.actionDeleteGrowLinePoint.triggered.connect(lambda: self._main_controller.set_mode(MODE_DELETE_GROW_LINE_POINT))
        self._ui.actionSelectDots.triggered.connect(lambda: self._main_controller.set_mode(MODE_SELECT_DOTS))
        self._ui.actionSelectGrowLineLayer.triggered.connect(lambda: self._main_controller.set_mode(MODE_SELECT_GROW_LINE_LAYER))
        self._ui.actionDeleteGrowLineLayer.triggered.connect(lambda: self._main_controller.set_mode(MODE_DELETE_GROW_LINE_LAYER))
        self._ui.actionSelectCenter.triggered.connect(lambda: self._main_controller.set_mode(MODE_SELECT_CENTER))

        # на клик по рабочему (второму) изображению делаем что-то в зависимости от выбранного режима
        self._ui.image2.mousePressEvent = lambda event: self._main_controller.process_second_image_clicked(event, self._ui.image2.pixmap().size(), self._ui.image2.size())
        self._main_controller.update_ui.connect(lambda: self.draw_image(2))

        # ввод номера ступени и снимка
        self._ui.inputLayerValue.returnPressed.connect(lambda: self._main_controller.go_to_layer(int(self._ui.inputLayerValue.text())))
        self._ui.inputImageNumber.returnPressed.connect(lambda: self._main_controller.go_to_image(int(self._ui.inputImageNumber.text())))
        
        #устанавливаем сигналы на изменения настроек пользователем
        self._ui.inputFileToSave.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))
        self._ui.inputTilt.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))
        self._ui.inputDivisionCount.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))
        self._ui.inputImageScaleNm.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))
        self._ui.inputSheetName.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))
        self._ui.inputGridSizeMultiplier.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))
        self._ui.inputCenterX.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))
        self._ui.inputCenterY.textChanged.connect(lambda text: self._model.update_attribute('excel_file', self._ui.inputFileToSave.text()))

        self._ui.gridRadialCheckbox.toggled.connect(lambda: self.on_grid_type_changed(0))
        self._ui.gridVerticalCheckbox.toggled.connect(lambda: self.on_grid_type_changed(1))
        self._ui.gridHorizontalCheckbox.toggled.connect(lambda: self.on_grid_type_changed(2))
        self._ui.gridEllipsoidCheckbox.toggled.connect(lambda: self.on_grid_type_changed(3))
        self._ui.checkboxShowOnImage.toggled.connect(self._main_controller.on_reverse_ui_toggled)

        #устанавливаем значения из модели
        self._ui.inputImageNumber.setText(str(self._model.current_image))
        self._ui.inputLayerValue.setText(str(self._model.current_layer))
        self._ui.inputFileToSave.setText(str(self._model.excel_file))
        self._ui.inputSheetName.setText(str(self._model.sheet_name))
        self._ui.inputTilt.setText(str(self._model.tilt))
        self._ui.inputDivisionCount.setText(str(self._model.division_count))
        self._ui.inputImageScaleNm.setText(str(self._model.nm_value))
        self._ui.inputGridSizeMultiplier.setText(str(self._model.grid_scale))
        self._ui.inputEllipsoidHeight.setText(str(self._model.elipse_width))
        self._ui.inputEllipsoidWidth.setText(str(self._model.elipse_height))
        self._ui.inputCenterX.setText(str(self._model.center_x))
        self._ui.inputCenterY.setText(str(self._model.center_y))
        self._ui.gridRadialCheckbox.setChecked(self._model.grid_type == 0)
        self._ui.gridVerticalCheckbox.setChecked(self._model.grid_type == 1)
        self._ui.gridHorizontalCheckbox.setChecked(self._model.grid_type == 2)
        self._ui.gridEllipsoidCheckbox.setChecked(self._model.grid_type == 3)
        self._ui.heckboxHalfInvisible.setChecked(self._model.half_grid)
        self._ui.checkboxSaveByHalf.setChecked(self._model.save_half)
        self._ui.checkboxInterpolation.setChecked(self._model.interpolation_enabled)

        self._ui.checkboxShowOnImage.setChecked(True)
        self._ui.checkboxMagnetEnabled.setChecked(True)
        self._ui.checkboxSelectGridLine.setChecked(False)

        #слушаем изменения в данных от сигналов из модели (те переменные, которые может изменить скрипт - №снимка, №ступени, координат x, y)
        self._model.attributeChanged.connect(self.on_variables_changed)
        self._model.attributeChanged.connect(lambda: self.draw_image(2))
        self._model.attributeChanged.connect(print("bebra"))

    def on_variables_changed(self):
        self._ui.inputLayerValue.setText(str(self._model.current_layer))
        self._ui.inputImageNumber.setText(str(self._model.current_image))
        self._ui.inputCenterX.setText(str(self._model.center_x))
        self._ui.inputCenterY.setText(str(self._model.center_y))

    def on_grid_type_changed(self, grid_type):
        if grid_type == self._model.grid_type:
            pass
        else:
            self._ui.gridRadialCheckbox.setChecked(self._model.grid_type == grid_type)
            self._ui.gridVerticalCheckbox.setChecked(self._model.grid_type == grid_type)
            self._ui.gridHorizontalCheckbox.setChecked(self._model.grid_type == grid_type)
            self._ui.gridEllipsoidCheckbox.setChecked(self._model.grid_type == grid_type)
            self._model.update_attribute('grid_type', int(grid_type))

    def open_image_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Выберите папку')
        if folder:
            self._main_controller.image_folder_selected(folder)
            self.draw_image(2) #HZ

    def open_folder_to_crop(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self._main_controller.crop_images(folder)

    def browse_excel_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть файл', '', "Excel files (*.xlsx *.xls)")
        if fname[0]:
            self.ui.inputFileToSave.setText(fname[0])
        
    def save_settings(self): #TODO del
        pass

    @pyqtSlot()
    def draw_ui_images(self): 
        self.draw_image(1)
        self.draw_image(2)

    @pyqtSlot(int) 
    def draw_image(self, image_number): #TODO

        current_image = self._model.current_image
        current_layer = self._model.current_layer
        crystal_object = self._model.crystal_object[current_image]


        imageLabel = self._ui.image1 if image_number == 1 else self._ui.image2
        pixmap = imageLabel.pixmap()
        path = os.path.join(self._model.image_folder, self._model.photos[self._model.current_image])
        print(path)
        print(self._model.photos[self._model.current_image])

        pixmap = QPixmap(path) 
        imageLabel.setPixmap(pixmap)
        if self._model.ui_enabled:
            # нарисовать номер картинки и название файла
            painter = QPainter(pixmap)
            font = QFont("Arial", 13)
            painter.setFont(font)            
            pen = QPen(QColor(255, 255, 255))
            painter.setPen(pen)

            painter.drawText(pixmap.width() * 9 / 10, pixmap.height() * 14 / 15,
                                f"{self._model.current_image + 1}")
            
            pen.setWidth(2)
            nm_value = self._model.nm_value
            step_size = max(nm_value // 10, 1)

            # Рисуем вертикальную шкалу делений с подписями
            for i in range(0, nm_value, step_size):
                y_pos = int((i / nm_value) * pixmap.height())
                painter.drawText(8, y_pos, str(nm_value - i))
                painter.drawLine(0, y_pos, 15, y_pos)

            # Рисуем горизонтальную шкалу делений с подписями
            for i in range(0, nm_value, step_size):
                x_pos = int((i / nm_value) * pixmap.width())
                painter.drawText(x_pos, pixmap.height() - 8, str(i))
                painter.drawLine(x_pos, pixmap.height(), x_pos, pixmap.height() - 15)

            # рассчитать координаты сетки и нарисовать её
            lines = fill_grid_lines(self._model.grid_type, pixmap.width(), pixmap.height(), self._model.division_count,
                            QPoint(self._model.center_x, self._model.center_y), self._model.tilt, self._model.grid_scale, self._model.elipse_width, self._model.elipse_height)

            self._main_controller.grid_lines = lines #TODO

            for id, value in enumerate(lines):
                if self._model.half_grid and id % 2 == 0 or not self._model.half_grid:
                    painter.drawLine(value[0], value[1])

                one_third_x = (2 * value[0].x() + value[1].x()) / 3
                one_third_y = (2 * value[0].y() + value[1].y()) / 3

                painter.drawText(one_third_x, one_third_y, f"{id + 1}")

            #если выбраны линии роста то нарисовать их
            growth_lines = crystal_object.growth_lines

            if growth_lines:
                painter.setPen(pen)
                curr_subarray = 0
                for subarray in growth_lines:
                    for index, point in enumerate(subarray):
                        if index == 0:
                            painter.setPen(QPen(Qt.black, 3)) # первая точка
                        elif index == len(subarray) - 1:
                            painter.setPen(QPen(Qt.cyan, 3)) # последняя точка
                        else:
                            painter.setPen(QPen(Qt.white, 3)) # все остальные
                        painter.drawEllipse(point, 6.5, 6.5) 

                    if len(subarray) > 3:
                        reconstructed_growth_lines = cubic_spline_interpolation(subarray)
                        if curr_subarray == self._model.current_layer:
                            pen = QPen(Qt.red, 3)
                            painter.setPen(pen)
                        else:
                            pen = QPen(Qt.black, 3)
                            painter.setPen(pen)
                        path = QPainterPath()
                        path.moveTo(subarray[0])
                        for i in range(1, len(reconstructed_growth_lines)):
                            path.lineTo(reconstructed_growth_lines[i])
                        painter.drawPath(path)
                    curr_subarray += 1

        #рисуем точки
        points = crystal_object.get_points_to_draw()

        painter.setPen(QPen(Qt.red, 4))
        for id, point in enumerate(points):
            if current_layer == points[id][0]:
                painter.setPen(QPen(Qt.blue, 3))
            else:
                painter.setPen(QPen(Qt.yellow, 3))
            painter.drawEllipse(point[2], 5, 5)

        #если есть точка которую двигаем то подсветить её
        point_to_move = self._main_controller.selected_grow_line_point_to_move
        if point_to_move:
            painter.setPen(QPen(Qt.blue, 3))
            point_list = crystal_object.get_values_by_grow_layer(current_layer)
            closestPoint = None
            minDistance = float('inf')
            for point in crystal_object.growth_lines[current_layer]:
                distance = (point - point_to_move).manhattanLength()
                if distance < minDistance:
                    minDistance = distance
                    closestPoint = point

            painter.drawEllipse(closestPoint, 6, 6)
            font = QFont("Arial", 25)
            painter.setFont(font)
            painter.drawText(10, pixmap.height() - 50, "Двигайте")

        painter.end()
        imageLabel.setPixmap(pixmap)
        # if self.current_image >=1:
        #     self.draw_events_prev()

    # @pyqtSlot(int)
    # def on_amount_changed(self, value):
    #     self._ui.spinBox_amount.setValue(value)

    # @pyqtSlot(str)
    # def on_even_odd_changed(self, value):
    #     self._ui.label_even_odd.setText(value)

    # @pyqtSlot(bool)
    # def on_enable_reset_changed(self, value):
    #     self._ui.pushButton_reset.setEnabled(value)

    # @pyqtSlot(list)
    # def on_list_changed(self, value):
    #     self._ui.listWidget_names.clear()
    #     self._ui.listWidget_names.addItems(value)