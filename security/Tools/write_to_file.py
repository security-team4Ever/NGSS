#!/bin/python2
#-*-coding:utf-8-*-

import json
from Security.Log.log import logger1

"""docstrings
This module for write data to localfile.

HOW TO USE:
    see source code
"""


class Write:
   
    def __init__(self, file_name = "result.json"):
        self.file_name = file_name
        self.logger = logger1


    def write_to_file(self, content, mode = "a+"):
        """
        content list like this:[CVE-1-1,CVE-2-2]
        content dict list this:{"CVE-1-1":{"description": "xxxxx", "monitor_time": "2021-xx-xx", "poc":"poc1, poc2, poc3, ..."}}
        """        
        w_str = "\n"
        fp = open(self.file_name, mode)
        try:
            if isinstance(content, list):
                for cve in content:
                    w_str += cve.strip() + "\n"

                fp.write(w_str)
                fp.close()
            elif isinstance(content, dict):
                json_str = "\n\n" + json.dumps(content, indent = 4)
                fp.write(json_str)
                fp.close()
            else:
                self.logger.error("Unknown data format,this func just support list or dict type")
        
        except Exception as e:
            self.logger.error("[Error] %s" % e)
            fp.close()
            pass


