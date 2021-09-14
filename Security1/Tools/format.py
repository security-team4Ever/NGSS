#!/bin/python2
#-*-coding:utf-8-*-


"""docstrings
This module for get format html string,

HOW TO USE:
    see source code
"""
       

class FormatString:
    
    def __init__(self, source_link = "", title = ""):
        self.source_link = source_link
        self.title = title


    def get_total_info(self, total_count):
        total_info = ""
        total_info += '<h1 style="text-align:center">%s</h1>' % self.title
        total_info += '<table align="center" style="border:1px solid black" width="960px">\
                          <tr align="center" style="border:1px solid black">\
                              <th style="border:1px solid black">Total Update CVE Count</th>\
                              <th style="border:1px solid black">CVE Source</th>\
                          </tr>\
                          <tr align="center" style="border:1px solid black">\
                              <td style="border:1px solid black">%s</td>\
                              <td style="border:1px solid black"><a href=%s>%s</a></td>\
                          </tr>\
                      </table>'  % (total_count, self.source_link, self.source_link)

        total_info += "<hr/>"
        
        return total_info


    @staticmethod
    def get_section_info(cvss_score, poc_list, description, cve_id):
        section_info = "<p>CVE&nbsp;ID:</p>"
        section_info += "<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s</p>" % cve_id
        section_info += "<p>Description:</p>"
        section_info += "<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s</p>" % description
        section_info += "<p>CVSS&nbsp;Score:</p>"
        section_info += "<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s</p>" % cvss_score
        section_info += "<p>POC&nbsp;LINK:</p>"

        for poc in poc_list:
            section_info += "<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href=%s>%s</a></p>" % (poc,poc)

        section_info += "<br/>"

        return section_info


    @staticmethod
    def get_section_title(title,total_count):
        section_title = "<p><strong>%s&nbsp;&nbsp;%s</strong></p>" % (title,total_count)
       
        return section_title


