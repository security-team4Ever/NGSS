#!/bin/python2
#-*-coding:utf-8-*-

import logging


"""docstrings
This module for get format logging instance,

HOW TO USE:
    see source code
"""


class Log:
    
    def __init__(self, level = logging.INFO, log_file = "log.txt", log_format = "%(asctime)s - %(filename)s:%(lineno)s - [%(levelname)s] : %(message)s"):
        self.level = level
        self.log_file = log_file
        self.format = log_format

    
    def get_logger(self):
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(self.level)
        
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(self.level)

        formatter = logging.Formatter(self.format)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        return self.logger
               
