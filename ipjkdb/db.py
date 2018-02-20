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

from google.appengine.ext import ndb
from summoner import Summoner
import webapp2



fronthtml = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="../default.css">
    <title>통합 패작 도감</title>
</head>
<body>
    <div id="page">
        <div id="header">
                <h1>통합 패작 도감</h1>
            
            <div id="bar">
                <div class="link">
                    <a href="../">홈</a>
                </div>
                <div class="link">
                    <a href="../db">도감</a>
                </div>
            </div>
        </div>"""
import htmltools

class MainPage(webapp2.RequestHandler):

    def get(self):

        self.response.write(fronthtml)
        summonerdata = memcache.get("summonerdata")
        if not summonerdata:
            dic = {}
            summoners = Summoner.query().fetch(key_only=True)
            for k in summoners:
                info = k.get()
                dic[info.SummonerName] = str(info.SummonerID)
            tmplist = sorted(dic)
            newdic = {}
            for items in tmplist:
                newdic[items] = dic[items]
            memcache.add("summonerdata", newdic)
        else:
            for key, value in summonerdata.iteritems():
                self.response.write(htmltools.getContent('<a href="../summoner?SummonerID=%d">%s</a>'%(value, key)))
                self.response.write(htmltools.getFooter())






app = webapp2.WSGIApplication([
    ('/db', MainPage)

], debug=True)