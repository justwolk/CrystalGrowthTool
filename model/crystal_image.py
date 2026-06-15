class CrystalImage:
    def __init__(self, image_path):
        self.image_path = image_path
        self.growth_lines = []
        self.grid_lines = []
        self.points = {}
        self.not_interacted_image = True
        self.center_x = None
        self.center_y = None
    
    def set_interacted(self):
        self.not_interacted_image = False

    def set_point(self, layer, line_idx, value):
        self.points[(layer, line_idx)] = value

    def clear_all_points(self):
        self.points = {}

    def clear_points_for_layer(self, layer):
        keys_to_remove = [k for k in self.points.keys() if k[0] == layer]
        for k in keys_to_remove:
            del self.points[k]

    def get_points_to_draw(self):
        if isinstance(self.points, dict):
            unique_points = [(layer, line_idx, value) for (layer, line_idx), value in self.points.items()]
            return unique_points
        return []

    def set_grid_lines(self, lines):
        self.grid_lines = lines
    
    def clear_grid_lines(self):
        self.grid_lines = []
