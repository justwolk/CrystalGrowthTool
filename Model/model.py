# from PyQt5.QtCore import QObject, pyqtSignal

# class TextNumberModel(QObject):
#     selectedImageChanged = pyqtSignal(str)

#     def __init__(self):
#         super().__init__()
#         self._current_image = 0

#     @property
#     def current_image(self):
#         return self._current_image

#     @current_image.setter
#     def text_number(self, value):
#         if self._current_image != value:
#             self._current_image = value
#             self.selectedImageChanged.emit(self._current_image)

#     def update_selected_image(self, new_number):
#         self._current_image = new_number


#     @property
#     def text_number(self):
#         return self._current_image

#     @text_number.setter
#     def text_number(self, value):
#         if self._current_image != value:
#             self._current_image = value
#             self.selectedImageChanged.emit(self._current_image)

#     def update_selected_image(self, new_number):
#         self._current_image = new_number


# from PyQt5.QtCore import QObject, pyqtSignal

# from Model.settings import Settings

# class TextNumberModel(QObject):
#     selectedImageChanged = pyqtSignal(str)
#     modeChanged = pyqtSignal(int)
#     levelChanged = pyqtSignal(int)



#     def __init__(self):
#         super().__init__()
#         self._attributes = {
#             'current_image': 0,
#             'mode': 0,
#             'level': 1
#         }

#     def __getattr__(self, name):
#         if name in self._attributes:
#             return self._attributes[name]
#         raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

#     def __setattr__(self, name, value):
#         if name.startswith('_'):
#             super().__setattr__(name, value)
#         else:
#             if name in self._attributes and self._attributes[name] != value:
#                 self._attributes[name] = value
#                 signal = getattr(self, f'{name}Changed', None)
#                 if signal:
#                     signal.emit(value)
#             else:
#                 raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

#     def update_attribute(self, name, new_value):
#         if name in self._attributes:
#             setattr(self, name, new_value)


#######################

import configparser
import json
import os
from PySide6.QtCore import Signal as pyqtSignal, Slot as pyqtSlot, QPoint, QObject
from Model.settings import Settings

class Model(QObject):
    attributeChanged = pyqtSignal(str, object)

    uiVariableUpdate = pyqtSignal(str, object)
    uiImageUpdate = pyqtSignal(str, object)


    def __init__(self):
        super(Model, self).__init__()

        self._attributes = {
            'image_folder': "",
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
            'interpolation_enabled': False,
            'ui_enabled': True,
            'magnet_enabled': True,
            'override_line': False,

        }

        self.selected_points = {}
        self.selected_growth_lines = []
        self.crystal_object = None
        self.photos = None

        # @property
        # def photos(self):
        #     return self._photos

        # @photos.setter
        # def photos(self, value):
        #     if value is not None and not isinstance(value, list):
        #         raise ValueError("Photos must be a list")
        #     self._photos = value

        home_dir = os.path.expanduser('~') 
        settings_dir = os.path.join(home_dir, 'Documents/crystal')
        settings_file_name = 'settings_file.json'

        settings_dir = os.path.join(home_dir, settings_dir)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir) 
        self.settings_file = os.path.join(settings_dir, settings_file_name)
        if not os.path.isfile(self.settings_file):
                    with open(self.settings_file, 'w') as json_file:
                        json.dump(self._attributes, json_file)
                    print(f"Created {self.settings_file}")
        # Load settings from JSON file
        self.load_from_json(self.settings_file)

        #self.settings = Settings('Documents/crystal', 'settings_file.ini')

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


    # def __setattr__(self, name, value):
    #     if name == '_attributes':
    #         super(Model, self).__setattr__(name, value)
    #     elif name in self._attributes:
    #         if self._attributes[name] != value:
    #             self._attributes[name] = value
    #             self.attributeChanged.emit(name, value)
    #     else:
    #         super(Model, self).__setattr__(name, value)

    
    def save_to_json(self, file_path):
        with open(file_path, 'w') as json_file:
            json.dump(self._attributes, json_file)

    def load_from_json(self, file_path):
        with open(file_path, 'r') as json_file:
            self._attributes = json.load(json_file)
            for key, value in self._attributes.items():
                setattr(self, key, value)

    def check_save_file_exist(self):
        if not os.path.isfile(self.settings_file):
            self.save_to_json(self.settings_file)
        else:
            self.load_from_json(self.settings_file)


    
