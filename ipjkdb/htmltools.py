# -*- coding: utf-8
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Nitro
#
# Created:     14-05-2015
# Copyright:   (c) Nitro 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#to print, use self.responce.write("Text to print")
# to get form values, use self.request.get("tag")
#use both of the under def post(self) on MainHandler
def getHeader():
    header = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="../default.css">
    <title>통합 패작 도감</title>
</head>
    </head>

    <body>
        <div id="page">

            <div id="header">
                <h1>통합 패작 도감</h1>
            </div>
            <div id="bar">
                <div class="link">
                    <a href="../">홈</a>
                </div>
                <div class="link">
                    <a href="../db">도감</a>
                </div>
            </div>
      
    """
    return(header)

def getContentTitle(title):
    titleformat = """
    <div class="contentTitle">%s</div>
    """%(str(title))
    return titleformat
def getContent(dat):
    defaultcontentformat = """
    <div class="contentText">%s</div>
    """%(str(dat))
    return defaultcontentformat
def getFooter():
    defaultfooter = """
    </div><div id="footer"></div></body></html>
    """
    return defaultfooter