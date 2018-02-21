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
import htmltools
import random
import time
from google.appengine.api import memcache
from google.appengine.ext import ndb
html1 = """
<hr>
<p>
커뮤니티 도감은 도감에 기록되어 있지 않지만 패작러인 소환사들을 위한 도감입니다. 특성상 소환사의 세부정보 등은 입력받지 않고, 오로지 
소환사 이름과 등재 횟수만 기록합니다
</p>
<br>
"""
searchform = """
<hr>
<form method="post" action="communitydb">
    <input type="text" name="summonername", placeholder="소환사 이름">
    <input type="hidden" name="action" value="search">
    <input type="submit" value="찾기">
</form>
<br>"""
registerform = """
<hr>
<p>명백한 패작행위를 하는 소환사들만 등재해주시기 바랍니다.먼저 전적검색을 이용해 꼭 확인해주세요</p>
<form method="post" action="communitydb">
    <input type="text" name="summonername", placeholder="소환사 이름">
    <input type="hidden" name ="action" value="register">
    <input type="submit" value="등재">
</form>
<br>"""
def generate_random_id():
    hashval = random.randint(1, 183532)
    ctime = int(time.time())+hashval
    return ctime

class CommunitySummoner(ndb.Model):
    SummonerName = ndb.StringProperty()
    SummonerID = ndb.IntegerProperty()
    SummonerHits = ndb.IntegerProperty()
class MainPage(webapp2.RequestHandler):

    def get(self):

        self.response.write(htmltools.getHeader())
        self.response.write(htmltools.getContentTitle("<h3>커뮤니티 도감</h2>"))
        self.response.write(htmltools.getContent(html1))
        self.response.write(htmltools.getContentTitle("<h1>커뮤니티 도감 검색</h1>"))
        self.response.write(htmltools.getContent(searchform))
        self.response.write(htmltools.getContentTitle("<h1>커뮤니티 도감 등재</h1>"))
        self.response.write(htmltools.getContent(registerform))
        self.response.write(htmltools.getFooter())
    def post(self):
        action = self.request.get("action")
        summonername = self.request.get("summonername")

        if not action or not summonername:
            self.redirect("../communitydb")

        if action == "search":
            if summonername == "Hide on bush":
                self.response.write(
                    "<script>alert('소환사 이름: %s\\n 모든 인간들을 패작하고 있습니다');document.location.href='/communitydb';</script>" % (summonername))
            else:
                query = CommunitySummoner.query(CommunitySummoner.SummonerName == summonername.encode()).fetch()
                summonername = summonername.encode()
                if query:
                    query = query[0]
                    self.response.write("<script>alert('소환사 이름: %s\\n 등재 횟수: %d');document.location.href='/communitydb';</script>"%(query.SummonerName.encode(), query.SummonerHits))
                else:
                    self.response.write("<script>alert('소환사 이름: %s\\n등재되지 않았습니다');document.location.href='/communitydb';</script>" % (summonername))
        elif action == "register":
            query = CommunitySummoner.query(CommunitySummoner.SummonerName == summonername.encode()).fetch()
            summonername = summonername.encode()
            clientip = str(self.request.remote_addr)
            if memcache.get(clientip):
                self.response.write("<script>alert('최근에 등재작업을 시행했습니다. 시간이 지난후 다시 등재가 가능힙니다.');document.location.href='/communitydb';</script>")
            else:
                if query:
                    query = query[0]
                    query.SummonerHits += 1
                    query.put()
                    memcache.add(clientip, 1, time=600)
                    self.response.write("<script>alert('소환사 이름: %s\\n이미 등재되었습니다. 등재 횟수가 1만큼 증가합니다\\n 등재 횟수: %d');document.location.href='/communitydb';</script>" % (
                        query.SummonerName.encode(), query.SummonerHits))
                else:
                    newsum = CommunitySummoner(SummonerName=summonername, SummonerID=generate_random_id(), SummonerHits=1)
                    newsum.put()
                    memcache.add(clientip, 1, time=600)
                    self.response.write("<script>alert('소환사 이름: %s\\n새로 등재되었습니다.\\n등재 횟수: %d');document.location.href='/communitydb';</script>" % (
                            summonername, 1))



app = webapp2.WSGIApplication([
    ('/communitydb', MainPage)

], debug=True)