from PySide2.QtCore import QPoint


class ImageViewportState:
    def __init__(self):
        self.scale = 1.0
        self.offset = QPoint(0, 0)
        self.min_scale = 0.8  # Позволяет отдалить до 80%
        self.max_scale = 10.0
        self.base_scale = 1.0
        self.panning = False
        self.last_pan_pos = None
        self.pixmap_size = None
        self.label_size = None

    def reset_pan(self):
        self.panning = False
        self.last_pan_pos = None

    def start_pan(self, pos):
        if self.scale <= 1.0:
            return False

        self.panning = True
        self.last_pan_pos = pos
        return True

    def update_pan(self, pos):
        if not self.panning or self.last_pan_pos is None:
            return False

        delta = pos - self.last_pan_pos
        self.offset += delta
        self.last_pan_pos = pos
        return True

    def zoom(self, delta, pos, label_width, label_height):
        old_scale = self.scale
        if delta > 0:
            new_scale = min(self.scale * 1.1, self.max_scale)
        else:
            new_scale = max(self.scale / 1.1, self.min_scale)

        # Магнит к 1.0 при попадании в диапазон 0.94-1.06
        if 0.95 <= new_scale <= 1.05:
            new_scale = 1.0
            self.offset = QPoint(0, 0)
            self.scale = new_scale
            return old_scale != new_scale or self.offset != QPoint(0, 0)

        if abs(old_scale - new_scale) < 1e-6:
            return False

        scale_factor = new_scale / old_scale

        if abs(new_scale - self.min_scale) < 1e-6:
            self.offset = QPoint(0, 0)
        else:
            offset_x = pos.x() - label_width / 2
            offset_y = pos.y() - label_height / 2
            self.offset = QPoint(
                int((self.offset.x() - offset_x) * scale_factor + offset_x),
                int((self.offset.y() - offset_y) * scale_factor + offset_y),
            )

        self.scale = new_scale
        return True

    def transform_point(self, point, center_x, center_y):
        scale = self.base_scale * self.scale
        x = point.x() * scale + center_x
        y = point.y() * scale + center_y
        return QPoint(int(x), int(y))
