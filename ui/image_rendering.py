import os

from PySide2.QtCore import QPoint, QPointF, Qt, Slot as pyqtSlot
from PySide2.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap

from utils.interpolate_curve import cubic_spline_interpolation as interpolate_curve_points


class ImageRenderingMixin:
    def draw_ui_images(self):
        self.draw_image(1)
        if self._model.current_image < len(self._model.photos):
            pixmap_path = os.path.join(self._model.image_folder, self._model.photos[self._model.current_image])
            pixmap = QPixmap(pixmap_path)
            self.draw_image(2)
            self._image2_pixmap_size = pixmap.size()
            self._image2_label_size = self._ui.image2.size()

    @pyqtSlot(int)
    def draw_image(self, image_number):
        current_image = self._model.current_image
        current_layer = self._model.current_layer
        draw_index = current_image

        if image_number == 1:
            if draw_index == 0:
                self._ui.image1.clear()
                return
            draw_index -= 1
            image_label = self._ui.image1
        else:
            image_label = self._ui.image2

        crystal_object = self._model.crystal_object[draw_index]
        path = os.path.join(self._model.image_folder, self._model.photos[draw_index])
        pixmap = QPixmap(path)

        if image_number == 2:
            display_pixmap, center_x, center_y = self._prepare_image2_display(pixmap)
            transform_func = lambda point: self._image2_handler.transform_point(point, center_x, center_y)
        else:
            display_pixmap, scale, offset_x, offset_y = self._prepare_image1_display(pixmap)
            transform_func = lambda point: QPoint(int(point.x() * scale + offset_x), int(point.y() * scale + offset_y))

        painter = QPainter(display_pixmap)
        if self._model.ui_enabled:
            self._draw_info_overlays(painter, pixmap, draw_index, transform_func)
            self._draw_grid(painter, crystal_object, transform_func)
            self._draw_growth_lines(painter, crystal_object, current_layer, transform_func)
            self._draw_points(painter, crystal_object, current_layer, transform_func)
            self._draw_move_point_indicator(painter, crystal_object, current_layer, transform_func)
            self._draw_center(painter, crystal_object, transform_func)
            self._draw_alt_mode_selection(painter, crystal_object, current_layer, transform_func)
        painter.end()

        image_label.setPixmap(display_pixmap)

    def _prepare_image2_display(self, pixmap):
        label_size = self._ui.image2.size()

        if pixmap.width() > 0 and pixmap.height() > 0:
            scale_x = label_size.width() / pixmap.width()
            scale_y = label_size.height() / pixmap.height()
            self._image2_handler.base_scale = min(scale_x, scale_y)
        else:
            self._image2_handler.base_scale = 1.0

        scale = self._image2_handler.base_scale * self._image2_handler.scale
        offset = self._image2_handler.offset

        scaled_pixmap = pixmap.scaled(
            int(pixmap.width() * scale),
            int(pixmap.height() * scale),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        display_pixmap = QPixmap(label_size)
        display_pixmap.fill(Qt.black)

        painter = QPainter(display_pixmap)
        center_x = display_pixmap.width() // 2 - scaled_pixmap.width() // 2 + offset.x()
        center_y = display_pixmap.height() // 2 - scaled_pixmap.height() // 2 + offset.y()
        painter.drawPixmap(center_x, center_y, scaled_pixmap)
        painter.end()

        self._image2_handler.pixmap_size = pixmap.size()
        self._image2_handler.label_size = label_size

        return display_pixmap, center_x, center_y

    def _prepare_image1_display(self, pixmap):
        label_size = self._ui.image1.size()

        if pixmap.width() <= 0 or pixmap.height() <= 0:
            display_pixmap = QPixmap(label_size)
            display_pixmap.fill(Qt.black)
            return display_pixmap, 1.0, 0, 0

        scale_x = label_size.width() / pixmap.width()
        scale_y = label_size.height() / pixmap.height()
        scale = min(scale_x, scale_y)

        scaled_pixmap = pixmap.scaled(
            label_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        display_pixmap = QPixmap(label_size)
        display_pixmap.fill(Qt.black)

        painter = QPainter(display_pixmap)
        offset_x = (label_size.width() - scaled_pixmap.width()) // 2
        offset_y = (label_size.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(offset_x, offset_y, scaled_pixmap)
        painter.end()

        return display_pixmap, scale, offset_x, offset_y

    def _draw_info_overlays(self, painter, pixmap, current_image, transform_func):
        font = QFont("Arial", 13)
        painter.setFont(font)
        pen = QPen(QColor(255, 255, 255))
        painter.setPen(pen)

        text_point = transform_func(QPoint(
            int(pixmap.width() * 7.5 / 9),
            int(pixmap.height() * 11 / 12),
        ))
        painter.drawText(text_point, f"{current_image + 1}/{self._model.photos[current_image]}")

        pen.setWidth(2)
        painter.setPen(pen)

        nm_value = self._model.nm_value
        step_size = max(nm_value // 10, 1)

        for i in range(0, nm_value, step_size):
            y_pos = int((i / nm_value) * pixmap.height())
            point = transform_func(QPoint(0, y_pos))
            painter.drawText(point.x() + 8, point.y(), str(nm_value - i))
            painter.drawLine(point.x(), point.y(), point.x() + 15, point.y())

        for i in range(0, nm_value, step_size):
            x_pos = int((i / nm_value) * pixmap.width())
            point = transform_func(QPoint(x_pos, pixmap.height()))
            painter.drawText(point.x(), point.y() - 8, str(i))
            painter.drawLine(point.x(), point.y(), point.x(), point.y() - 15)

    def _draw_grid(self, painter, crystal_object, transform_func):
        if not self._ui.checkbox_show_grid.isChecked():
            return

        lines = crystal_object.grid_lines
        if not lines:
            return

        grid_working_mode = self._ui.slider_work_with_grid_or_layer.value() == 99

        for line_idx, line in enumerate(lines):
            if not line or len(line) < 2:
                continue

            is_current_line = line_idx == self._model.current_grid_line
            if self._model.half_grid and line_idx % 2 == 0:
                continue

            if is_current_line and grid_working_mode:
                painter.setPen(QPen(QColor(255, 44, 123), 3))
            else:
                painter.setPen(QPen(QColor(255, 255, 255), 2))

            for i in range(len(line) - 1):
                painter.drawLine(transform_func(line[i]), transform_func(line[i + 1]))

            one_third_x = (2 * line[0].x() + line[-1].x()) / 3
            one_third_y = (2 * line[0].y() + line[-1].y()) / 3
            point = transform_func(QPoint(int(one_third_x), int(one_third_y)))
            painter.drawText(point.x(), point.y(), f"{line_idx + 1}")

        if not grid_working_mode:
            return

        for line_idx, line in enumerate(lines):
            if not line:
                continue

            is_current_line = line_idx == self._model.current_grid_line
            for point_idx, point in enumerate(line):
                if is_current_line:
                    if point_idx == 0:
                        painter.setPen(QPen(Qt.darkGreen, 3))
                    elif point_idx == len(line) - 1:
                        painter.setPen(QPen(Qt.darkMagenta, 3))
                    else:
                        painter.setPen(QPen(Qt.darkYellow, 3))
                else:
                    if point_idx == 0:
                        painter.setPen(QPen(Qt.green, 2))
                    elif point_idx == len(line) - 1:
                        painter.setPen(QPen(Qt.magenta, 2))
                    else:
                        painter.setPen(QPen(Qt.yellow, 2))

                painter.drawEllipse(transform_func(point), 4, 4)

    def _draw_growth_lines(self, painter, crystal_object, current_layer, transform_func):
        grid_working_mode = self._ui.slider_work_with_grid_or_layer.value() == 99
        growth_lines = crystal_object.growth_lines

        if not growth_lines:
            return
        if grid_working_mode and self._ui.checkbox_hide_everything_when_grid_edit.isChecked():
            return

        for layer_idx, line_points in enumerate(growth_lines):
            if not line_points:
                continue

            for point_idx, point in enumerate(line_points):
                display_point = self._get_display_point(point, layer_idx, point_idx, current_layer)

                if point_idx == 0:
                    painter.setPen(QPen(Qt.black, 2))
                elif point_idx == len(line_points) - 1:
                    painter.setPen(QPen(Qt.cyan, 2))
                else:
                    painter.setPen(QPen(Qt.white, 2))

                painter.drawEllipse(transform_func(display_point), 4, 4)

            self._draw_layer_line(painter, line_points, layer_idx, current_layer, transform_func)

    def _get_display_point(self, point, layer_idx, point_idx, current_layer):
        if (
            self._main_controller._dragging_layer_point
            and layer_idx == current_layer
            and point_idx == self._main_controller._dragged_point_index
            and self._main_controller._drag_preview_point is not None
        ):
            return self._main_controller._drag_preview_point
        return point

    def _draw_layer_line(self, painter, line_points, layer_idx, current_layer, transform_func):
        is_current = layer_idx == current_layer
        painter.setPen(QPen(Qt.red if is_current else Qt.black, 3))

        if len(line_points) > 3 and self._model.interpolation_enabled:
            points_to_draw = interpolate_curve_points(line_points)
        else:
            points_to_draw = line_points

        if len(points_to_draw) <= 1:
            return

        path = QPainterPath()
        path.moveTo(transform_func(points_to_draw[0]))
        for i in range(1, len(points_to_draw)):
            path.lineTo(transform_func(points_to_draw[i]))
        painter.drawPath(path)

    def _draw_points(self, painter, crystal_object, current_layer, transform_func):
        points = crystal_object.get_points_to_draw()
        if not points:
            return

        for layer, line_idx, point in points:
            painter.setPen(QPen(Qt.blue if current_layer == layer else Qt.yellow, 3))
            painter.drawEllipse(transform_func(point), 5, 5)

    def _draw_move_point_indicator(self, painter, crystal_object, current_layer, transform_func):
        point_to_move = self._main_controller.selected_grow_line_point_to_move
        if point_to_move is None or current_layer >= len(crystal_object.growth_lines):
            return

        point_list = crystal_object.growth_lines[current_layer]
        if not point_list:
            return

        painter.setPen(QPen(Qt.blue, 3))
        closest_point = min(point_list, key=lambda point: (point - point_to_move).manhattanLength())
        painter.drawEllipse(transform_func(closest_point), 6, 6)

        font = QFont("Arial", 25)
        painter.setFont(font)
        painter.drawText(10, painter.device().height() - 50, "Двигайте")

    def _draw_center(self, painter, crystal_object, transform_func):
        if crystal_object.center_x is None or crystal_object.center_y is None:
            return

        center_point = QPointF(crystal_object.center_x, crystal_object.center_y)
        painter.setPen(QPen(Qt.blue, 4))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(transform_func(center_point), 6, 6)

    def _draw_alt_mode_selection(self, painter, crystal_object, current_layer, transform_func):
        alt_state = self._main_controller.get_alt_mode_state()
        if not alt_state['active']:
            return

        if self._model.work_with_grid_mode:
            current_line = self._model.current_grid_line
            if current_line >= len(crystal_object.grid_lines):
                return
            points = crystal_object.grid_lines[current_line]
        else:
            if current_layer >= len(crystal_object.growth_lines):
                return
            points = crystal_object.growth_lines[current_layer]

        if not points:
            return

        selected_index = alt_state['selected_index1']
        if selected_index is not None and selected_index < len(points):
            transformed_point = transform_func(points[selected_index])

            painter.setPen(QPen(QColor(0, 255, 0), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(transformed_point, 12, 12)

            painter.setPen(QPen(QColor(255, 255, 0), 2))
            painter.drawEllipse(transformed_point, 7, 7)

        font = QFont("Arial", 14)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 0)))
        hint_text = "ALT: выберите 2 соседние точки"
        if selected_index is not None:
            hint_text = "ALT: выберите вторую соседнюю точку"
        painter.drawText(10, 30, hint_text)
