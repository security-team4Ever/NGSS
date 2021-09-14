#-*-coding:utf-8-*-


import os
import sys

# reload(sys)
# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))

import re
import requests
import json
import time
import datetime
import socks
import urllib
import threading
import threadpool
from bs4 import BeautifulSoup
from Security1.Tools import *
from Security1.Log.log import logger1


class Monitor(object):
    
    def __init__(self, proxy = {}, log = "monitor.log"):
        '''
        proxy_type just support int value: 
                   1 2 3 (1 is socks.SOCKS4 ,2 is socks.SOCKS5, 3 is socks.HTTP)
        proxy define : 
                   {"host" : ip, "port" : port, "user" : user, "passwd" : passwd, "proxy_type" : type}
        '''
        self.cve_list = []
        self.logger = logger1
        self.cve_poc = {}
        self.cve_description = {}
        self.cve_cvss_score = {}
        self.proxy = proxy

        if self.proxy:
            user = "" if not "user" in proxy.keys() else proxy['user']
            passwd = "" if not "passwd" in proxy.keys() else proxy['passwd']
                
            socks.setdefaultproxy(proxy['proxy_type'], proxy['host'], proxy['port'], user, passwd)
            socks.wrapmodule(urllib)
   

    #use get function to send request
    def get_response(self, url, header = {}, timeout = 60.0):
        if header:
            self.logger.info("Request url %s" % url)
            response = requests.get(url, headers = header, timeout = timeout)
        else:
            response = requests.get(url, timeout = timeout)

        return response.text


    def get_request_header(self, host):
        header = {
            "Host": host,
            "Connection": "close",
            "Cache-Control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                           AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/87.0.4280.88 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;\
                       q=0.9,image/avif,image/webp,image/apng,*/*;\
                       q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        return header

 
    #TODO
    def get_cve_info(self, cve_list, url = "https://nvd.nist.gov/vuln/detail/", threads = 20):
        '''
        api: https://services.nvd.nist.gov/rest/json/cve/1.0/ is so slowly, 
        search page: https://nvd.nist.gov/vuln/detail/ is more fast
        maybe the api will be deprecate in future
        more information to see nvd.nist.gov site        
        '''
        header = self.get_request_header("nvd.nist.gov")

        lock = threading.RLock()

        pool = threadpool.ThreadPool(threads)

        func_var = []
        for cve in cve_list:
            func_var.append(([cve, url, header, lock], None))

        requests = threadpool.makeRequests(self.set_cve_info, func_var)

        [pool.putRequest(req) for req in requests]
        pool.wait()
       

    #TODO
    def set_cve_info(self, cve, url, header, lock):
        url += cve
        try:
            time.sleep(2)
            f = time.time()
            response = self.get_response(url, header)

            nvd_soup = BeautifulSoup(response, 'lxml')
            
            cvss3_element = ""
            cvss2_element = ""
            can3_element = ""
            detail_element = ""
           
            if len(nvd_soup.select("#nistV3MetricHidden")) >= 1:
                cvss3_element = str(nvd_soup.select("#nistV3MetricHidden")[0])
            
            if len(nvd_soup.select("#nistV2MetricHidden")) >= 1:
                cvss2_element = str(nvd_soup.select("#nistV2MetricHidden")[0])

            if len(nvd_soup.select("#cnaV3MetricHidden")) >= 1:
                can3_element =  str(nvd_soup.select("#cnaV3MetricHidden")[0])

            if len(nvd_soup.select("#vulnDetailTableView")) >= 1:
                detail_element = str(nvd_soup.select("#vulnDetailTableView")[0])
                
            cvss3_re = re.search("vuln-cvssv3-base-score[\s\S]*?&gt;([\s\S]*?)&lt;/span&gt;",\
                                 cvss3_element)
            cvss2_re = re.search("vuln-cvssv2-base-score[\s\S]*?&gt;([\s\S]*?)&lt;/span&gt;",\
                                 cvss2_element)
            can3_re = re.search("vuln-cvssv3-base-score[\s\S]*?&gt;([\s\S]*?)&lt;/span&gt;",\
                                can3_element)
            desciption_re = re.search("vuln-description\">([\s\S]*?)</p>",\
                                      detail_element)

            if desciption_re != None:
                lock.acquire()
                self.cve_description[cve] = desciption_re.group(1).strip()
                lock.release()
                
                #like c++ inline func
                try:
                    cvss3_score = float(cvss2_re.group(1).strip())
                except:
                    cvss3_score = 0.0

                try:
                    cvss2_score = float(cvss2_re.group(1).strip())
                except:
                    cvss2_score = 0.0

                try:
                    can3_score = float(can3_re.group(1).strip())
                except:
                    can3_score = 0.0

                lock.acquire()
                self.cve_cvss_score[cve] = (cvss3_score, cvss2_score, can3_score)
                lock.release()
            else:
                self.logger.warning("Cant find cve description,cve %s" % cve)

        except Exception as e:
            print(e)
            self.logger.error("Request error, when request %s" % url, exc_info = True)

    
    def write_to_file(self, content, local_file = "monitor_result.txt", mode = "a+"):
        tools.Write(local_file = local_file).write_to_file(content = content, mode = mode)


    def write_to_mysql(self, host, port, user, passwd, db_name, table_name, vul_list):
        tools.Write(db_host = host, db_port = port, \
                    db_user = user, db_passwd = passwd, db_name = db_name).insert_mysql_value(table_name, vul_list)


    def write_to_es(self, host, port, user, passwd, index, content):
        es = tools.Write().get_es_conn(host, port, user, passwd)
        tools.Write().insert_es_data(index, content, es = es)
        
    
    #interface
    def handle_response(self, response_str):
        raise Exception("This function is a interface")

    
    #interface
    def get_poc(self):
        raise Exception("This function is a interface")


    #interface
    def set_poc_list(self):
        raise Exception("This function is a interface")


