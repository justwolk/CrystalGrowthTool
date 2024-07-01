from PySide6.QtCore import QPoint


class CrystalImage:
    def __init__(self, image_path):
        self.image_path = image_path
        self.growth_lines = []
        self.points = {}

    def set_point(self, x, y, value):
        self.points[(x, y)] = value

    def remove_point(self, x, y):
        if (x, y) in self.points:
            del self.points[(x, y)]
            #print(self.points)
        else:
            print(f"Point ({x}, {y}) does not exist.")


    def remove_point_by_index(self, grow_layer, index):
        keys_list = list(self.points.keys())

        if 0 <= index < len(keys_list):
            key_to_remove = keys_list[index]

            if key_to_remove in self.points:
                del self.points[key_to_remove]
                print(f"Removed point at index {index}: {key_to_remove}")
            else:
                print(f"Point {key_to_remove} does not exist.")
        else:
            print(f"Invalid index: {index}. Index must be within the range [0, {len(keys_list) - 1}].")


    def get_points(self):
        #print(f"selfpoints: {self.points}")
        unique_points = [(value, point) for value, point in self.points]
        return unique_points

    def get_points_to_draw(self):
        if isinstance(self.points, dict):
            unique_points = [(x, y, value) for (x, y), value in self.points.items()]
            #print("NOT ERROR")
            return unique_points
        else:
            print("Error: self.points is not a dictionary.")
            return []

    def get_points_by_grow_layer(self, layer):
        layer_points = [(x, y, value) for (x, y), value in self.points.items() if y == layer]
        return layer_points

    def get_values_by_grow_layer(self, layer):
        layer_values = [value for (x, y), value in self.points.items() if x == layer]
        return layer_values


    def add_growth_line(self, points):
        self.growth_lines.append(points)

    def to_dict(self):
        return {
            "image_path": self.image_path,
            "growth_lines": [list(map(lambda p: (p.x(), p.y()), line)) for line in self.growth_lines],
            "points": [(x, y, point.x(), point.y()) for (x, y), point in self.points.items()]        }

    
    @classmethod
    def from_dict(cls, data):
        crystal = cls(data["image_path"])
        crystal.growth_lines = [list(map(lambda p: QPoint(p[0], p[1]), line)) for line in data["growth_lines"]]
        crystal.points = {(index, id): QPoint(x, y) for index, id, x, y in data["points"]}
        return crystal
