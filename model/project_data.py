import atexit
import os

from PySide2.QtCore import QPointF, QObject
from PySide2.QtCore import Signal as pyqtSignal
from model.crystal_image import CrystalImage
from utils.grid_generator import GridType
from utils.crop_images import init_images as prepare_images
from utils.crystal_archive import CrystalArchive


class ProjectModel(QObject):
    attributeChanged = pyqtSignal(str, object)

    def __init__(self, project_file, do_crop=None, image_folder=None, project_name=None):
        super().__init__()

        self._attributes = {
            'current_image': 0,
            'current_layer': 0,
            'current_grid_line': 0,
            'work_with_grid_mode': False,
            'excel_file': 'sample.xlsx',
            'sheet_name': 'data',
            'division_count': 10,
            'tilt': 0,
            'grid_type': GridType.RADIAL.value,
            'nm_value': 10,
            'grid_scale': 1,
            'ellipse_width': 500,
            'ellipse_height': 1000,
            'center_x': 360,
            'center_y': 360,
            'half_grid': False,
            'save_half': False,
            'interpolation_enabled': False,
            'ui_enabled': True,
            'show_grid': True,
            'autosave': True,
            'checkbox_ask_new_image_copy': False,
            'checkbox_copy_grid': True,
            'checkbox_copy_layers': True,
            'excel_save_accuracy': 2,
        }

        self.crystal_object = None
        self.photos = None
        self.settings_file = None
        self.image_folder = None
        self._temp_dir = None
        self._archive = CrystalArchive()
        
        atexit.register(self._cleanup)

        #TODO исправить, кривая реализация
        # Open existing project / открыть проект
        if do_crop is None and image_folder is None and project_name is None:
            self.load_from_crystal(project_file)
        # Create a new project / создать проект
        else:
            self.create_new_project(project_file, do_crop, image_folder)

    def _cleanup(self):
        if self._temp_dir:
            self._archive.cleanup_temp_dir(self._temp_dir)

    def __getattr__(self, name):
        if '_attributes' in self.__dict__:
            if name in self._attributes:
                return self._attributes[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name == '_attributes':
            super().__setattr__(name, value)
        elif '_attributes' in self.__dict__ and name in self._attributes:
            if self._attributes[name] != value:
                self._attributes[name] = value
                self.attributeChanged.emit(name, value)
        else:
            super().__setattr__(name, value)

    def create_new_project(self, project_file, do_crop, image_folder):
        images = prepare_images(image_folder, do_crop=do_crop)
        self.photos = [f'img_{idx + 1}.png' for idx in range(len(images))]
        
        project_data = {
            'attributes': self._attributes,
            'data': [[] for _ in range(len(images))],
            'grids': [[] for _ in range(len(images))],
            'points': [{} for _ in range(len(images))]
        }
        
        self._archive.create_archive(project_file, project_data, images)
        
        self.load_from_crystal(project_file)

    def save_to_crystal(self):
        if not self.settings_file:
            return
            
        all_data_to_save = []
        all_grids_to_save = []
        all_points_to_save = []
        
        for i in range(len(self.photos)):
            data = self.crystal_object[i].growth_lines
            data_to_save = [[(point.x(), point.y()) for point in line] for line in data]
            all_data_to_save.append(data_to_save)
            
            grid = self.crystal_object[i].grid_lines
            grid_to_save = [[(point.x(), point.y()) for point in line] for line in grid]
            all_grids_to_save.append(grid_to_save)
            
            points = self.crystal_object[i].points
            points_to_save = {f"{layer},{line_idx}": (point.x(), point.y()) 
                            for (layer, line_idx), point in points.items()}
            all_points_to_save.append(points_to_save)

        project_data = {
            'attributes': self._attributes,
            'data': all_data_to_save,
            'grids': all_grids_to_save,
            'points': all_points_to_save,
            'centers': [{'x': obj.center_x, 'y': obj.center_y} for obj in self.crystal_object],
            'visited': [not obj.not_interacted_image for obj in self.crystal_object]
        }
        
        self._archive.update_archive(self.settings_file, project_data, self.image_folder)
        
        if self.autosave:
            print("Успешное автосохранение")

    def load_from_crystal(self, project_file):
        self.settings_file = project_file
        
        if self._temp_dir:
            self._archive.cleanup_temp_dir(self._temp_dir)
        
        try:
            project_data, images_dir, temp_dir = self._archive.load_archive(project_file)
            self._temp_dir = temp_dir
            self.image_folder = images_dir
            
            if 'attributes' in project_data:
                self._load_attributes(project_data['attributes'])
            
            self.photos = [file for file in os.listdir(images_dir) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]
            self.photos.sort()
            self.crystal_object = [CrystalImage(image_path) for image_path in self.photos]
            
            all_data = project_data.get('data', [])
            if len(all_data) == len(self.photos):
                for i in range(len(self.photos)):
                    self.crystal_object[i].growth_lines = [[QPointF(x, y) for x, y in line] for line in all_data[i]]
            
            all_grids = project_data.get('grids', [])
            if len(all_grids) == len(self.photos):
                for i in range(len(self.photos)):
                    self.crystal_object[i].grid_lines = [[QPointF(x, y) for x, y in line] for line in all_grids[i]]
            
            all_points = project_data.get('points', [])
            if len(all_points) == len(self.photos):
                for i in range(len(self.photos)):
                    points_dict = {}
                    for key_str, (x, y) in all_points[i].items():
                        layer, line_idx = map(int, key_str.split(','))
                        points_dict[(layer, line_idx)] = QPointF(x, y)
                    self.crystal_object[i].points = points_dict
            
            all_centers = project_data.get('centers', [])
            if len(all_centers) == len(self.photos):
                for i in range(len(self.photos)):
                   center_data = all_centers[i]
                   self.crystal_object[i].center_x = center_data.get('x')
                   self.crystal_object[i].center_y = center_data.get('y')
            
            visited_list = project_data.get('visited', [])
            if len(visited_list) == len(self.photos):
                for i in range(len(self.photos)):
                    self.crystal_object[i].not_interacted_image = not visited_list[i]

            for key, value in self._attributes.items():
                setattr(self, key, value)
                
        except Exception as e:
            print(f"Ошибка загрузки проекта: {e}")
            raise

    def update_attribute(self, name, new_value):
        if name in self._attributes:
            setattr(self, name, new_value)

    def _load_attributes(self, attributes):
        legacy_names = {
            'elipse_width': 'ellipse_width',
            'elipse_height': 'ellipse_height',
        }

        for key, value in attributes.items():
            target_key = legacy_names.get(key, key)
            if target_key in self._attributes:
                self._attributes[target_key] = value
