# -*- coding:utf-8 -*-

import os
# import logging
import logging.config
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logconfig.yml")
with open(CONFIG_PATH, "r") as f:
    dict_conf = yaml.safe_load(f)

logging.config.dictConfig(dict_conf)
root = logging.getLogger()
logger1 = logging.getLogger('logger1')