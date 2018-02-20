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

import os
import webapp2
import random
import time
from google.appengine.ext import ndb
import htmltools

registerhtml = """
<form method="post" action="../summoner">
    <input type="text" placeholder="소환사 이름" name="SummonerName">
    <textarea rows="10" cols="100" maxlength="1400" name="SummonerInfo"></textarea>
    <input type="submit" value="전송">
</form>
"""

def generate_random_id():
    hashval = random.randint(1, 183532)
    ctime = int(time.time())+hashval
    return ctime
class Summoner(ndb.Model):
    SummonerName = ndb.StringProperty()
    SummonerInfo1 = ndb.StringProperty()
    SummonerInfo2 = ndb.StringProperty()
    SummonerID = ndb.IntegerProperty()

def split_utf8(s):
    n = 1500
    if len(s) <= n:
        return s, ""
    while ord(s[n]) >= 0x80 and ord(s[n]) < 0xc0:
        n -= 1
    return s[0:n], s[n:]

class MainPage(webapp2.RequestHandler):
    def get(self):
        summonerid = self.request.get("SummonerID")
        method = self.request.get("method")
        if method == "add":
            self.response.write(htmltools.getHeader())
            self.response.write(htmltools.getContentTitle("<h2>%s</h2>" % "패작러 정보 추가".encode("utf-8")))
            self.response.write(htmltools.getContent(registerhtml))
            self.response.write(htmltools.getFooter())
        elif not summonerid:
            self.redirect("../db")
        else:
            query = Summoner.query(Summoner.SummonerID==int(summonerid)).get()
            if query:
                self.response.write(htmltools.getHeader())
                self.response.write(htmltools.getContentTitle("<h2>%s</h2>"%query.SummonerName.encode("utf-8")))
                self.response.write(htmltools.getContent('<br><div style="white-space: pre-line;">%s%s</div>'%(query.SummonerInfo1.encode("utf-8"),
                                                                        query.SummonerInfo2.encode("utf-8"))))
                self.response.write(htmltools.getFooter())
            else:
                self.redirect("../db")
    def post(self):

        summonername = self.request.get("SummonerName")
        summonerinfo = self.request.get("SummonerInfo")
        info1, info2 = split_utf8(summonerinfo.encode("utf-8"))
        if not info2: info2 = ""

        summonerid = generate_random_id() + len(summonername)
        Summoner(SummonerName=summonername, SummonerInfo1=info1, SummonerInfo2=info2, SummonerID=summonerid).put()
        self.redirect("../")



app = webapp2.WSGIApplication([
    ('/summoner', MainPage)

], debug=True)