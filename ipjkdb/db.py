# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Copyright 2016 Google Inc.
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
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


import htmltools
from google.appengine.ext import ndb
from google.appengine.api import memcache
from summoner import Summoner
from collections import OrderedDict
import webapp2
import pickle
import logging


fronthtml = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="../css/default.css">
    <title>통합 패작 도감</title>
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
            <div class="link">
                    <a href="../analyzeusers">패작러 추적 프로젝트</a>
                </div>
            <div class="link">
                    <a href="../communitydb">커뮤니티 도감</a>
                </div>
        </div>
"""


class MainPage(webapp2.RequestHandler):

    def get(self):

        self.response.write(fronthtml)
        self.response.write(htmltools.getContentTitle("<h2>패작러 목록</h2>"))
        self.response.write(htmltools.getContent("<h3>2018.5.31 수정</h3><p>현재 패작도감은 관리가 되지 않는 상태이며, 등재된 패작러 중 상당수는 삭제 또는 닉변된 계정 혹은 패작유저 여부가 논란에 있습니다.</p><br>"))
        self.response.write('<div class="ContentText"><ul>')
        summonerdata = memcache.get("summonerdata")
        if not summonerdata:
            dic = OrderedDict()
            summoners = Summoner.query().order(Summoner.SummonerName).fetch(keys_only=True)
            for k in summoners:
                info = k.get()
                dic[info.SummonerName] = info.SummonerID
            memcache.add("summonerdata", dic)


            for key, value in dic.iteritems():
                self.response.write('<li><a href="../summoner?SummonerID=%s">%s</a></li>'%(value, key))

        else:
            for key, value in summonerdata.iteritems():
                self.response.write('<li><a href="../summoner?SummonerID=%s">%s</a></li>'%(value, key))
        self.response.write('</ul></div>')
        self.response.write(htmltools.getFooter())






app = webapp2.WSGIApplication([
    ('/db', MainPage)
], debug=True)