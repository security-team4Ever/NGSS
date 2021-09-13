import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")

def get_config():
    fp = open(CONFIG_PATH)
    data = yaml.load(fp, Loader = yaml.FullLoader)
    return data


global_config = get_config()
