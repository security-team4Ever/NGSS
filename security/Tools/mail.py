#!/bin/python2
#-*-coding:utf-8-*-


import smtplib
import time
import socks
import os
import sys

reload(sys)
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../config"))

import threading
import email
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from log import Log
from config import global_config


"""docstrings
This module for get send mail function,

HOW TO USE:
    see source code
"""

       
class Mail:

    #static value
    defalut_port = [25, 465, 587]    
    useable_port = []

    def __init__(self):
        self.server = None
        data = global_config['mail']
        proxy = global_config['proxy']

        try:           
            self.mail_host = data['mail_host']
            self.mail_user = data['mail_user']
            self.mail_port = data['mail_port']
            self.mail_passwd = data['mail_passwd']
            self.logger = Log(log_file = data['log_file']).get_logger() if data['log_file'] else Log(log_file = "log/mail.log").get_logger()

            if proxy['use_proxy'] and proxy['proxy_host'] != None:
                #write to smtp.log                        
                self.logger.info("Set proxy:[%s %s]" % (proxy['proxy_host'], proxy['proxy_port']))
                socks.setdefaultproxy(Mail.get_proxy_type(proxy['proxy_type']), proxy['proxy_host'], proxy['proxy_port'], \
                                     proxy['proxy_user'], proxy['proxy_passwd'])
                socks.wrapmodule(smtplib)
            elif data['use_proxy']:
                raise Exception("set proxy need to use 'mail_config.yml' to set proxy info.")
        except Exception as e:              
            print "[Error]: When init instance get error %s " % e
        
    
    @staticmethod
    def get_proxy_type(p_type):
        if p_type.lower() == "socks5":
            return socks.SOCKS5
        elif p_type.lower() == "http":
            return socks.HTTP
        elif p_type.lower() == "socks4":
            return socks.SOCKS4
        else:
            raise Exception("proxy type %s unknown!" % p_type)

    
    @staticmethod
    def set_useable_port(host, timeout = 2.0):       
        lock = threading.RLock()
        threads = [] 
        for port in Mail.defalut_port:
            th = threading.Thread(target=Mail.connect, args=(host, port, timeout, lock))
            th.start()
            threads.append(th)

        for t in threads:
            t.join()

   
    @staticmethod 
    def connect(host, port, timeout ,lock):
        try:
            smtp = smtplib.SMTP(timeout = timeout)
            smtp.connect(host, port)
            smtp.close()
            lock.acquire()
            Mail.useable_port.append(port)
            lock.release()
        except Exception as e:
            return

    
    def set_mail_co(self, timeout = 20.0):
        try:
            if self.mail_port == 25:
                self.logger.info("Set connect with [%s %s]" % (self.mail_host, self.mail_port))
                self.server = smtplib.SMTP(self.mail_host, self.mail_port, timeout = timeout)

                self.logger.info("Login [%s %s], use [%s] account" % (self.mail_host, self.mail_port, \
                                 self.mail_user))
                self.server.login(self.mail_user, self.mail_passwd)
            elif self.mail_port == 465:
                self.logger.info("Set connect with [%s %s]" % (self.mail_host, self.mail_port))
                self.server = smtplib.SMTP_SSL(self.mail_host, self.mail_port, timeout = timeout)
                
                #self.server.set_debuglevel(1)
                self.logger.info("Login [%s %s], use [%s] account" % (self.mail_host, self.mail_port, \
                                 self.mail_user))
                self.server.login(self.mail_user, self.mail_passwd)
            elif self.mail_port == 587:
                self.logger.info("Set connect with [%s %s]" % (self.mail_host, self.mail_port))
                self.server = smtplib.SMTP(self.mail_host, self.mail_port, timeout = timeout)

                #self.server.set_debuglevel(1)
                self.server.ehlo()
                self.logger.info("Login [%s %s], use [%s] account" % (self.mail_host, self.mail_port, \
                                 self.mail_user))
                self.server.starttls()
                self.server.ehlo() #again
                self.server.login(self.mail_user, self.mail_passwd)
            else:
                raise Exception("Unknown smtp port, not in [25,465,587] list.")
        except Exception as e:
            if self.server:
                self.server.quit()
            print "[Error]: %s" % e
            self.logger.error("Failed to login server [%s %s] with [%s] account" % (self.mail_host, \
                                                                                    self.mail_port, \
                                                                                    self.mail_user), \
                                                                                    exc_info = True)
            exit(1)
        

    def send_mail(self, subj, cont, mailto_list, ccto_list, att_list= [], ishtml = False, timeout = 60.0):
        mailto = ";".join(mailto_list)
        ccto = ";".join(ccto_list)

        self.set_mail_co(timeout)
        
        main_msg = MIMEMultipart()
        if ishtml:
            text_msg = MIMEText(cont, 'html', 'utf-8')
        else:
            text_msg = MIMEText(cont, 'plain', 'utf-8')

        main_msg.attach(text_msg)

        if att_list:
            for att in att_list:
                file_con = open(att, "rb")
                file_msg = MIMEBase("application", "octet-stream", filename = os.path.basename(att))
                file_msg.add_header("Content-Disposition", "attachment", filename = os.path.basename(att))
                file_msg.set_payload(file_con.read())
                encoders.encode_base64(file_msg)
                main_msg.attach(file_msg)
        
        main_msg["From"] = self.mail_user
        main_msg["To"] = mailto
        main_msg["Cc"] = ccto
        main_msg["Subject"] = subj
        main_msg['Date'] = email.Utils.formatdate()
        
        try:
            self.logger.info("Begin send mail to %s , ccto %s" % (mailto, ccto) )
            self.server.sendmail(self.mail_user, mailto_list + ccto_list, main_msg.as_string())
            self.logger.info("Send mail finished")
            self.server.quit()
        except Exception as e:
            if self.server:
                self.server.quit()
            self.logger.error("Send mail failed", exc_indo = True)

a = Mail()
a.send_mail("asd","asd",["sdujsfeng@163.com"],[]) 
