"""
This file contains the configuration class.
"""
import json
import os
import re


class Config_file:
    def __init__(self, cfg_file: str = ''):
        """
        Initialize the Config_file class.

        By default, sets the **default configuration**. If doesn't have
        the a configuration file, the defualt_config() method sets

        Args:
            cfg_file (str, optional): File path to json configurations. Defaults to ''.
        """
        self.default_config()
        # if cfg_file != '' and os.path.isfile(cfg_file):
        #     self.load_cfg(cfg_file)
        # else:
        #     self.__config_file = self.__default
        self.load_cfg(cfg_file)
        # self.validate()

    def change_cfg(self, parameter: str, new_value):
        """
        Change configuration of some parameter.
        Args:
            parameter (str): Name of parameter to be changed.
            new_value (_type_): New value to be setted.
        """
        if not isinstance(parameter, str):
            raise ValueError('The parameter is not a string.')
        elif not parameter in self.default.keys():
            raise ValueError('This is not a valid key.')
        elif type(new_value) is not type(self.default[parameter]):
            raise ValueError('Invalid parameter type.')
        else:
            self.config[parameter] = new_value
            self.validate()

    def load_cfg(self, path: str = ''):
        empty_file = path == ''
        if not empty_file:
            if os.path.isdir(path):
                raise ValueError('This is a folder, not a config json.')
            elif not os.path.isfile(path):
                raise ValueError('This file does not exist.')
            elif self.json_validator(path) == False:
                raise ValueError('Invalid config file.')
            else:
                self.__file = open(path, mode='r', encoding='utf-8')
                self.__config_file = json.load(self.__file)
                self.validate()
        else:
            self.__config_file = self.__default

    def json_validator(self, path=''):
        try:
            json_file = open(file=path, mode='r', encoding='utf-8')
            json.load(json_file)
            return True
        except ValueError as err:
            return False

    # @property
    def get_cfg(self, parameter: str):
        return self.config[parameter]

    @property
    def config(self):
        return self.__config_file['config']

    def save(self, path=''):
        json_save = json.dumps(self.__config_file, indent=4)
        if os.path.isdir(path):
            raise ValueError('This path is a directory.')
        with open(path, mode='w', encoding='utf-8') as f:
            f.write(json_save)

    def validate(self):
        for default in self.default:
            if default not in self.config.keys():
                default_value = self.default[default]
                self.change_cfg(parameter=default, new_value=default_value)

    @property
    def default(self):
        return self.__default['config']

    def default_config(self):
        self.__default = {}
        self.__default['config'] = {}
        default = self.__default['config']

        # Default values
        # project_folder=os.path.abspath(pathlib.Path(__file__).parent)
        project_folder = os.path.abspath('app')
        # project_folder=re.sub("\\\\",  "/",  project_folder)

        template_folder = project_folder + '/templates/'

        if not os.path.exists(project_folder):
            os.mkdir(project_folder)
        if not os.path.exists(template_folder):
            os.mkdir(template_folder)

        default.setdefault('DEFAULT_TEMPLATE', 'template_html.html')
        default.setdefault('IMG_FOLDER', 'img/')
        default.setdefault('TEMPLATE_FOLDER', template_folder)
        default.setdefault('DEFAULT_COLOR', [1.0, 1.0, 0.0])
        default.setdefault('INTERSECTION_LEVEL', 0.1)
        default.setdefault('COLUMNS', 1)
        default.setdefault('TOLERANCE', 0.1)
        default.setdefault('ADJUST_COLOR', True)
        default.setdefault('ADJUST_DATE', True)
        default.setdefault('ADJUST_TEXT', True)
        default.setdefault('IMAGE', True)
        default.setdefault('INK', True)
        default.setdefault('ADJUST_COLOR', True)
