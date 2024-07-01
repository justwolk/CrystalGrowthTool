import configparser
import os

class Settings:
    def __init__(self, settings_directory, settings_file_name):
        self.default_settings = {
            'DEFAULT': {
                'excel_file': 'sample.xlsx',
                'sheet_name': 'data',
                'lines_count': 15,
                'tilt': 0,
                'grid_type': 0,
                'show_nm': True,
            }
        }
        
        home_dir = os.path.expanduser('~') 
        settings_dir = os.path.join(home_dir, settings_directory)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir) 
        self.settings_file = os.path.join(settings_dir, settings_file_name)
        
        self.config = configparser.ConfigParser()
        self.check_settings()

    def check_settings(self):
        if not os.path.isfile(self.settings_file):
            self.config.read_dict(self.default_settings)
            self.save_settings()
        else:
            self.load_settings()

    def load_settings(self):
        self.config.read(self.settings_file)

    def save_settings(self):
        with open(self.settings_file, 'w') as file:
            self.config.write(file)

    def get_setting(self, section, key):
        return self.config.get(section, key)

    def set_setting(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save_settings()

######
# settings = Settings('settings_file.ini')
# settings.set_setting('DEFAULT', 'count', '3')
# settings.set_setting('DEFAULT', 'var', '4')
# settings.set_setting('DEFAULT', 'file', 'file.txt')
# settings = Settings('settings_file.ini')
# count = settings.get_setting('DEFAULT', 'count')
# var = settings.get_setting('DEFAULT', 'var')
# file = settings.get_setting('DEFAULT', 'file')
