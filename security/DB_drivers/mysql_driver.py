#!/bin/python3
# -*-coding:utf-8-*-

import sys
import os

base_path = os.path.abspath(os.path.abspath(os.path.dirname(os.getcwd())))
sys.path.append(base_path)


import pymysql
from Security.Config.config import global_config

"""docstrings
This module for write data to mysql.

HOW TO USE:
    see source code
"""


class Mysql:

    def __init__(self):
        data = global_config.get('mysql')
        self.db_host = data.get('db_host', '127.0.01')
        self.db_user = data.get('db_user')
        self.db_passwd = data.get('db_passwd')
        self.db_name = data.get('db_name')
        self.db_port = data.get('db_port', '3306')
        self.cursor = None
        self.db = None

    def get_mysql_db_cursor(self):
        if not self.db_host:
            raise Exception("use get_mysql_db_cursor need to set db_host when get Write instance")

        try:
            self.db = pymysql.connect(self.db_host, self.db_user, self.db_passwd, port=self.db_port, charset="utf8")
            self.cursor = self.db.cursor()
        except Exception as e:
            if self.cursor:
                self.cursor.close()
            print("[Error] %s" % e)

        return self.cursor if self.cursor else None

    def set_mysql_db(self, db_name):
        try:
            self.get_mysql_db_cursor()
            # fake sqli protect
            sql = pymysql.escape_string("create database if not exists %s" % db_name)
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print("[Error]%s" % e)

    def create_mysql_table(self, table_name, value_dict, pri_key, db_name=""):
        db_name = self.db_name if db_name == "" else db_name
        try:
            self.get_mysql_db_cursor()
            # fake sqli protect
            sql = pymysql.escape_string("use %s" % db_name)
            self.cursor.execute(sql)

            value_str = ""
            count = 0
            value_len = len(value_dict.keys())
            for value in value_dict.keys():
                count += 1
                value_str += value + " " + value_dict[value]
                if count < value_len:
                    value_str += ","

            sql2 = pymysql.escape_string("create table if not exists %s (%s , PRIMARY KEY (%s))" \
                                         % (table_name, value_str, pri_key))
            self.cursor.execute(sql2)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            print("[Error]%s" % e)

    def create_mysql_index(self, table_name, col_list, index_name, db_name=""):
        db_name = self.db_name if db_name == "" else db_name
        try:
            self.get_mysql_db_cursor()
            # fake sqli protect
            sql = pymysql.escape_string("use " % db_name)
            self.cursor.execute(sql)

            value_str = ""
            count = 0
            value_len = len(col_list)
            for value in col_list:
                count += 1
                value_str += value
                if count < value_len:
                    value_str += ","

            sql2 = pymysql.escape_string("create index %s on %s (%s)" % (index_name, table_name, value_str))
            self.cursor.execute(sql2)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            print("[Error]%s" % e)

    def insert_mysql_value(self, table_name, vul_list, db_name=""):
        db_name = self.db_name if db_name == "" else db_name
        try:
            self.get_mysql_db_cursor()
            # fake sqli protect
            sql = pymysql.escape_string("use %s" % db_name)
            self.cursor.execute(sql)

            value_str = ""
            count = 0
            value_len = len(vul_list)
            for value in vul_list:
                count += 1
                value_str += value
                if count < value_len:
                    value_str += ","

            sql2 = ("insert into %s values (%s)" % (table_name, value_str))
            print(sql2)
            self.cursor.execute(sql2)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            print("[Error]%s" % e)

    def close_mysql_co(self):
        if self.db:
            self.db.close()



