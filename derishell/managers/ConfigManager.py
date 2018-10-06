import os
import jsonpickle

from derishell.util.Util import Util

from derishell.models.ConfigModel import ConfigModel


class ConfigManager:

    @staticmethod
    def get_config():
        if os.path.isfile("config.json"):
            file = open("config.json", "r") 
            return jsonpickle.decode(file.read())
        else:
            Util.get_logger().debug("No configuration found generating new one")
            ConfigManager.create_config()
            file = open("config.json", "r") 
            return jsonpickle.decode(file.read())
            
    @staticmethod
    def create_config():
        file = open("config.json", "w")
        file.write(jsonpickle.encode(ConfigModel()))
        file.close()

    @staticmethod
    def update_config(model):
        file = open("config.json", "w")
        file.write(jsonpickle.encode(model))
        file.close()
