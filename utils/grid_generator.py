import math
import numpy as np
from enum import Enum
from PySide2.QtCore import QPointF

class GridType(Enum):
    RADIAL = 0
    VERTICAL = 1
    HORIZONTAL = 2
    ELLIPSOID = 3

def build_grid_lines(grid_type, image_width, image_height, division_count, center, tilt, grid_scale, ellipse_width, ellipse_height):
    grid_scale = float(grid_scale)

    lines = []

    if grid_type == GridType.RADIAL.value:
        lines = generate_radial_grid(image_width, image_height, division_count, center, tilt, grid_scale)
    elif grid_type == GridType.VERTICAL.value:
        lines = generate_vertical_grid(image_width, image_height, division_count, center, tilt, grid_scale)
    elif grid_type == GridType.HORIZONTAL.value:
        lines = generate_horizontal_grid(image_width, image_height, division_count, center, tilt, grid_scale)
    elif grid_type == GridType.ELLIPSOID.value:
        lines = generate_ellipsoid_grid(image_width, image_height, division_count, center, tilt, grid_scale, ellipse_width, ellipse_height)

    return lines

def generate_radial_grid(image_width, image_height, division_count, center, tilt, grid_scale):
    lines = []
    start_offset = 0.05
    base_radius = min(image_width, image_height) / 2
    scaled_radius = base_radius * grid_scale

    for angle in np.linspace(0, 360, division_count, endpoint=False):
        angle_with_tilt = angle + tilt
        rad = math.radians(angle_with_tilt)
        start_point = QPointF(
            center.x() + start_offset * scaled_radius * math.cos(rad),
            center.y() + start_offset * scaled_radius * math.sin(rad)
        )
        end_point = QPointF(
            center.x() + scaled_radius * math.cos(rad),
            center.y() + scaled_radius * math.sin(rad)
        )
        lines.append([start_point, end_point])

    return lines

def generate_vertical_grid(image_width, image_height, division_count, center, tilt, grid_scale):
    lines = []

    base_width = image_width / 2
    grid_width = base_width * grid_scale
    spacing = (2 * grid_width) / division_count

    start_x_rel = -grid_width
    extension = math.sqrt(image_width**2 + image_height**2) * grid_scale

    tilt_rad = math.radians(tilt)
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)

    for i in range(division_count):
        x_rel = start_x_rel + i * spacing

        x1_rot = x_rel * cos_t - (-extension) * sin_t
        y1_rot = x_rel * sin_t + (-extension) * cos_t

        x2_rot = x_rel * cos_t - (extension) * sin_t
        y2_rot = x_rel * sin_t + (extension) * cos_t

        lines.append([
            QPointF(center.x() + x1_rot, center.y() + y1_rot),
            QPointF(center.x() + x2_rot, center.y() + y2_rot)
        ])

    return lines

def generate_horizontal_grid(image_width, image_height, division_count, center, tilt, grid_scale):
    lines = []

    base_height = image_height / 2
    grid_height = base_height * grid_scale
    spacing = (2 * grid_height) / division_count

    start_y_rel = -grid_height
    extension = math.sqrt(image_width**2 + image_height**2) * grid_scale

    tilt_rad = math.radians(tilt)
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)

    for i in range(division_count):
        y_rel = start_y_rel + i * spacing

        x1_rot = (-extension) * cos_t - y_rel * sin_t
        y1_rot = (-extension) * sin_t + y_rel * cos_t

        x2_rot = extension * cos_t - y_rel * sin_t
        y2_rot = extension * sin_t + y_rel * cos_t

        lines.append([
            QPointF(center.x() + x1_rot, center.y() + y1_rot),
            QPointF(center.x() + x2_rot, center.y() + y2_rot)
        ])

    return lines

def generate_ellipsoid_grid(image_width, image_height, division_count, center, tilt, grid_scale, ellipse_width, ellipse_height):
    lines = []

    base_a = ellipse_width / 2
    base_b = ellipse_height / 2

    scaled_a = base_a * grid_scale
    scaled_b = base_b * grid_scale

    tilt_rad = math.radians(tilt)
    cos_tilt = math.cos(tilt_rad)
    sin_tilt = math.sin(tilt_rad)

    for angle in np.linspace(0, 360, division_count, endpoint=False):
        t_rad = math.radians(angle)

        local_x = scaled_a * math.cos(t_rad)
        local_y = scaled_b * math.sin(t_rad)

        rotated_x = local_x * cos_tilt - local_y * sin_tilt
        rotated_y = local_x * sin_tilt + local_y * cos_tilt

        x = center.x() + rotated_x
        y = center.y() + rotated_y

        start_point = QPointF(center.x(), center.y())
        end_point = QPointF(x, y)
        lines.append([start_point, end_point])

    return lines
