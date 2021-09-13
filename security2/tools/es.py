#!/bin/python2
#-*-coding:utf-8-*-

import os
import sys

reload(sys)
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../config"))

from elasticsearch import Elasticsearch
from config import global_config

"""docstrings
This module for write data to es.

HOW TO USE:
    see source code
"""


class Es:
   
    def __init__(self):
        data = global_config['es']
        self.db_host = data['es_host']
        self.db_user = data['es_user'] if data['es_user'] else ""
        self.db_passwd = data['es_passwd'] if data['es_passwd'] else ""
        self.db_port = data['es_port']

    
    #es database used to ref: https://blog.csdn.net/qq_43076825/article/details/108404335
    def get_es_conn(self):
        es = Elasticsearch(
             http_auth = (self.db_user, self.db_passwd),
             host = self.db_host, port = self.db_port)

        return es

    
    #es index like mysql database
    def create_es_index(self, es_index, es = ""):
        es = self.get_es_conn() if es == "" else es
        try:
            es.indices.create(index = es_index)
        except Exception as e:
            print "[Error] %s" % "when create es index,get error: %s" % e
        

    def insert_es_data(self, es_index, content, doc_type = "_doc", es = ""):
        '''
        content is list([dict1,dict2]) or dict
        '''
        es = self.get_es_conn() if es == "" else es
        try:
            if type(content) is list:
                es.bulk(index = es_index, doc_type = doc_type, body = content)
            elif type(content) is dict:
                es.index(index = es_index, doc_type = doc_type, body = content)
            else:
                raise Exception("insert_es_data func just support list or dict to insert")

        except Exception as e:
            print "[Error]%s" % e


    def get_field_from_es(self, es_index, field_list, es = "", start = 0, depth = 10):
        '''
        this func return dict like:
        {u'hits': {u'hits': [{u'_source': {u'CVE': u'CVE-0000-0000'}}, \
        {u'_source': {u'CVE': u'CVE-0000-0001'}}, {u'_source': \
        {u'CVE': u'CVE-0000-0002'}}]}} 
        '''
        es = self.get_es_conn() if es == "" else es
        try:
            body = {"from": start, "size": depth}
            filter_path = []
            for field in field_list:
                filter_path.append("hits.hits._source."  + field)
            print filter_path
            data = es.search(index = es_index, filter_path = filter_path, body = body)
            return data
        except Exception as e:
            print "[Error]%s" % e


    def search_from_es(self, es_index, field, value, multi = False, fuzz = True, es = ''):
        es = self.get_es_conn() if es == "" else es
        try:
            body = {}
            if fuzz:
                if multi:
                    if type(field) is not list:
                        raise Exception("Use fuzz search and multi field,need set list type' field")
                    else:
                        field_list = [f for f in field]             
                        body = {
                                "query":{
                                   "multi_match":{
                                       "query" : value, 
                                       "fields": field_list
                                    }
                                 }
                               }
                        data = es.search(index = es_index, body = body)
                        return data
            
                else:
                    body = {
                            "query":{
                                "match":{
                                    field : value
                                }
                             }
                           }
                    data = es.search(index = es_index, body = body)
                    return data
            else:
                if multi:
                    if type(value) is not list:
                        raise Exception("Use exact search and multi field, need set list type' value")
                    else:
                        value_list = [v for v in value]
                        body = {
                                "query":{
                                    "terms":{
                                        field + ".keyword" : value_list
                                    }
                                }
                               }
                        data = es.search(index = es_index, body = body)  
                        return data
                else:
                    body = {
                            "query":{
                                "term":{
                                    field + ".keyword" : value
                                }
                            }
                           }
                    data = es.search(index = es_index, body = body)
                    return data
        except Exception as e:
            print "[Error]%s" % e

