import math
from PySide6.QtCore import QPointF
import numpy as np

def fill_grid_lines(grid_type, width, height, lines_count, center, tilt, grid_scale, elipse_width, elipse_height):

    width = width * grid_scale
    height = height * grid_scale

    offset_x = center.x() - width / 2
    offset_y = center.y() - height / 2

    half_grid_offset_x = width / lines_count / 2
    half_grid_offset_y = height / lines_count/ 2

    offset = QPointF(offset_x, offset_y)

    lines = []

    if grid_type == 0:
        start_offset = 0.05
        radius = min(width, height)
        for idx, angle in enumerate(np.linspace(0, 360, lines_count, endpoint=False)):
            start_point = QPointF(center.x() + start_offset * radius * math.cos(math.radians(angle)),
                                  center.y() + start_offset * radius * math.sin(math.radians(angle)))
            edge_point = QPointF(center.x() + radius * math.cos(math.radians(angle)),
                                 center.y() + radius * math.sin(math.radians(angle)))
            lines.append((start_point, edge_point))
        return lines

    if grid_type == 1:
        tilt_angle_rad = math.radians(tilt)
        for i in range(lines_count):
            x_pos = int((i / lines_count) * height)
            start_point = QPointF(x_pos + offset_x + half_grid_offset_x, 0 + offset_y)
            edge_point = QPointF(x_pos + offset_x + half_grid_offset_x, height + offset_y)

            # Перевести точки в начало координат перед поворотом
            start_point_translated = QPointF(start_point.x() - center.x(), start_point.y() - center.y())
            edge_point_translated = QPointF(edge_point.x() - center.x(), edge_point.y() - center.y())

            # Поворот
            rotated_start_point = QPointF(
                start_point_translated.x() * math.cos(tilt_angle_rad) - start_point_translated.y() * math.sin(tilt_angle_rad),
                start_point_translated.x() * math.sin(tilt_angle_rad) + start_point_translated.y() * math.cos(tilt_angle_rad)
            )
            rotated_edge_point = QPointF(
                edge_point_translated.x() * math.cos(tilt_angle_rad) - edge_point_translated.y() * math.sin(tilt_angle_rad),
                edge_point_translated.x() * math.sin(tilt_angle_rad) + edge_point_translated.y() * math.cos(tilt_angle_rad)
            )

            # Перевести обратно после вращения
            rotated_start_point = QPointF(rotated_start_point.x() + center.x(), rotated_start_point.y() + center.y())
            rotated_edge_point = QPointF(rotated_edge_point.x() + center.x(), rotated_edge_point.y() + center.y())

            lines.append((rotated_start_point, rotated_edge_point))
        return lines


    if grid_type == 2:
        tilt_angle_rad = math.radians(tilt)
        for i in range(lines_count):
            y_pos = int((i / lines_count) * width)
            start_point = QPointF(0 + offset_x, y_pos + offset_y + half_grid_offset_y)
            edge_point = QPointF(width + offset_x, y_pos + offset_y + half_grid_offset_y)

            start_point_translated = QPointF(start_point.x() - center.x(), start_point.y() - center.y())
            edge_point_translated = QPointF(edge_point.x() - center.x(), edge_point.y() - center.y())

            rotated_start_point = QPointF(
                start_point_translated.x() * math.cos(tilt_angle_rad) - start_point_translated.y() * math.sin(tilt_angle_rad),
                start_point_translated.x() * math.sin(tilt_angle_rad) + start_point_translated.y() * math.cos(tilt_angle_rad)
            )
            rotated_edge_point = QPointF(
                edge_point_translated.x() * math.cos(tilt_angle_rad) - edge_point_translated.y() * math.sin(tilt_angle_rad),
                edge_point_translated.x() * math.sin(tilt_angle_rad) + edge_point_translated.y() * math.cos(tilt_angle_rad)
            )

            rotated_start_point = QPointF(rotated_start_point.x() + center.x(), rotated_start_point.y() + center.y())
            rotated_edge_point = QPointF(rotated_edge_point.x() + center.x(), rotated_edge_point.y() + center.y())

            lines.append((rotated_start_point, rotated_edge_point))
        return lines
    
    if grid_type == 3:
        a = elipse_width 
        b = elipse_height

        for i in range(lines_count):
            angle = 2 * math.pi * i / lines_count
            x1 = center.x() + a * math.cos(angle)
            y1 = center.y() + b * math.sin(angle)
            x2 = center.x() - a * math.cos(angle)
            y2 = center.y() - b * math.sin(angle)
            lines.append((QPointF(x1, y1), QPointF(x2, y2)))
        return lines
