import yaml
import os
from Security1.Log.log import logger1

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")

def get_config():
    fp = open(CONFIG_PATH)
    data = yaml.load(fp, Loader = yaml.FullLoader)
    return data

try:
    global_config = get_config()
except Exception as e:
    logger1.error(e)
