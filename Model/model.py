import configparser
import json
import os
from PySide6.QtCore import Signal as pyqtSignal, Slot as pyqtSlot, QPoint, QObject
from Model.crystal import CrystalImage
from Modules.crop_images import crop_images
from PIL import Image

class Model(QObject):
    attributeChanged = pyqtSignal(str, object)

    uiVariableUpdate = pyqtSignal(str, object)
    uiImageUpdate = pyqtSignal(str, object)

    def __init__(self, project_folder, do_crop = None, image_folder = None, project_name = None):
        super(Model, self).__init__()

        self._attributes = {
            #'image_folder': "",
            'current_image': 0,
            'current_layer': 0,
            'excel_file': 'sample.xlsx',
            'sheet_name': 'data',
            'division_count': 10,
            'tilt': 0,
            'grid_type': 0,
            'nm_value': 10,
            'grid_scale': 1,
            'elipse_width': 500,
            'elipse_height': 1000,
            'center_x': 360,
            'center_y': 360,
            'show_nm': True,
            'half_grid': False,
            'save_half': False,
            'interpolation_enabled': True,
            'ui_enabled': True,
            'magnet_enabled': True,
            'override_line': 0,
            'transfer_next_image': True,
        }
        self.data = None
        self.selected_points = {}
        self.selected_growth_lines = []
        self.crystal_object = None
        self.photos = None
        self.settings_file = None

        self.current_folder = None
        self.image_folder = None

        #если открыт уже созданный проект
        if do_crop == None and image_folder == None and project_name == None: 
            self.load_from_json(project_folder)
            self.current_folder = project_folder
        
        #если создан новый проект
        else:
            self.create_new_project(project_folder, do_crop, image_folder, project_name)
            project_dir = os.path.join(project_folder, project_name)
            self.load_from_json(project_dir)
            self.current_folder = project_dir

        self.image_folder = os.path.join(self.current_folder, 'images')


    def create_new_project(self, project_folder, do_crop, image_folder, project_name):
        #создать папку проекта
        new_project_dir = os.path.join(project_folder, project_name)
        if not os.path.exists(new_project_dir):
            os.makedirs(new_project_dir) 

        #создать пустой json
        settings_file = os.path.join(new_project_dir, 'settings.json')
        if not os.path.isfile(settings_file):
            with open(settings_file, 'w') as json_file:
                json.dump({'attributes': self._attributes, 'data': []}, json_file)
            print(f"Created {settings_file}")

        # Обрезать изображения, если их нужно обрезать
        images = None
        if do_crop:
            images = crop_images(image_folder, do_crop=True)
        else:
            images = crop_images(image_folder, do_crop=False)
        self.photos = images

        #скопировать изображения в папку проекта
        new_project_image_dir = os.path.join(new_project_dir, "images")

        if not os.path.exists(new_project_image_dir):
            os.makedirs(new_project_image_dir) 
        
        for idx, img in enumerate(images):
                img.save(os.path.join(new_project_image_dir, f'img_{idx + 1}.png'))
   
    def save_to_json(self):
        file_path = self.settings_file
        all_data_to_save = []

        for i in range(len(self.photos)):
            data = self.crystal_object[i].growth_lines
            data_to_save = [[(point.x(), point.y()) for point in line] for line in data]
            all_data_to_save.append(data_to_save)

        with open(file_path, 'w') as json_file:
            json.dump({'attributes': self._attributes, 'data': all_data_to_save}, json_file)

    def load_from_json(self, project_path):
        settings = self.settings_file = os.path.join(project_path, "settings.json")

        with open(settings, 'r') as json_file:
            loaded_data = json.load(json_file)
            if 'attributes' in loaded_data:
                self._attributes = loaded_data['attributes']

                image_folder = os.path.join(project_path, "images")
                self.image_folder = image_folder
                self.photos = [file for file in os.listdir(image_folder) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]
                self.photos.sort()
                self.crystal_object = [CrystalImage(image_folder) for image_folder in self.photos]

                all_data = loaded_data.get('data', [])
                if len(all_data) != len(self.photos):
                    #print(f"Error: Mismatch between number of images ({len(self.photos)}) and data entries ({len(all_data)})")
                    pass

                for i in range(len(self.photos)):
                    self.crystal_object[i].growth_lines = [[QPoint(x, y) for x, y in line] for line in all_data[i]]

                for key, value in self._attributes.items():
                    setattr(self, key, value)
            else:
                print(f"Выберите правильный проект, {project_path} содержит ошибки")

    def check_save_file_exist(self):
        if not os.path.isfile(self.settings_file):
            self.save_to_json()
        else:
            self.load_from_json(self.settings_file)

    def __getattr__(self, name):
        if '_attributes' in self.__dict__:
            if name in self._attributes:
                return self._attributes[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        if name == '_attributes':
            super(Model, self).__setattr__(name, value)
        elif name in self._attributes:
            if self._attributes[name] != value:
                self._attributes[name] = value
                #if name in ['image_folder', 'current_image', 'current_layer']: 
                self.attributeChanged.emit(name, value)
        else:
            super(Model, self).__setattr__(name, value)

    def update_attribute(self, name, new_value):
        if name in self._attributes:
            setattr(self, name, new_value)

    def set_point(self, x, y, value):
        self.points[(x, y)] = value

    def remove_point(self, x, y):
        if (x, y) in self.points:
            del self.points[(x, y)]

    def add_growth_line(self, x, y):
        self.growth_lines.append((x, y))

    def remove_growth_line(self, x, y):
        if (x, y) in self.growth_lines:
            self.growth_lines.remove((x, y))