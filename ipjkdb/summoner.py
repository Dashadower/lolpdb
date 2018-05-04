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


import webapp2
import random
import time
from google.appengine.ext import ndb
from google.appengine.api import memcache
from collections import OrderedDict
import htmltools
from urllib import quote

registerhtml = """
<form method="post" action="../summoner">
    <input type="text" placeholder="소환사 이름" name="SummonerName">
    <input type="text" placholder="등급" name="SummonerGrade">
    <textarea rows="10" cols="100" maxlength="4000" name="SummonerInfo">정보없음</textarea>
    <input type="submit" value="전송">
</form>
"""
midhtml = """
<form method="POST" action="../register">
    <input type="hidden" value="%s" name="SummonerID">
    <input type="text" maxlength="50" placeholder="한줄정보 입력(지나친 욕설 삭제합니다)" size="50" name="comment">
    <input type="submit" value="등록">
</form>
<hr>
"""

summonerinfohtml = """
<table>
    <tr>
        <td>티어(업데이트 일자: %s)</td>
        <td> %s</td>
    </tr>
    <tr>
        <td>랭크 승률</td>
        <td>%d%%(%s)</td>
    </tr>
</table>
<button onclick="document.location.href='/riotapi?summonerid=%s'">정보 갱신하기</button>
"""
opggbutton = """<button onclick="document.location.href='http://www.op.gg/summoner/userName=%s'">OP.GG</button>"""

def generate_random_id():
    hashval = random.randint(1, 183532)
    ctime = int(time.time())+hashval
    return ctime
class Summoner(ndb.Model):
    SummonerName = ndb.StringProperty()
    SummonerInfo = ndb.TextProperty()
    SummonerID = ndb.IntegerProperty()
    SummonerGrade = ndb.StringProperty()
    UserComments = ndb.TextProperty()
    RiotID = ndb.StringProperty()
    SummonerTier = ndb.StringProperty()
    SummonerWinRate = ndb.IntegerProperty()
    SummonerGameInfo = ndb.StringProperty()
    APIUpdateTime = ndb.StringProperty()
    APIUpdateTime_int = ndb.IntegerProperty()
def split_utf8(s):
    n = 1500
    if len(s) <= n:
        return s, "", ""
    while ord(s[n]) >= 0x80 and ord(s[n]) < 0xc0:
        n -= 1
    if len(s[n:]) > 1500:
        rerun = split_utf8(s[n:])
        return s[0:n], rerun[0], rerun[1]
    else:
        return s[0:n], s[n:], ""

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
                if query.APIUpdateTime == None:
                    self.redirect("../riotapi?summonerid=%s"%(summonerid))
                else:
                    self.response.write(htmltools.getHeader())

                    self.response.write(htmltools.getContentTitle("<h2>%s</h2>"%query.SummonerName.encode("utf-8")))
                    self.response.write(htmltools.getContent(summonerinfohtml%(query.APIUpdateTime.encode("utf-8"),query.SummonerTier.encode("utf-8"), query.SummonerWinRate,query.SummonerGameInfo.encode(), query.SummonerID)))
                    self.response.write(htmltools.getContent(opggbutton%(quote(query.SummonerName.encode("utf-8")))))
                    self.response.write(htmltools.getContent("<br>"))
                    self.response.write(htmltools.getContentTitle("<h4>도감에 등록된 정보</h4>"))
                    self.response.write(htmltools.getContent('<hr><div style="white-space: pre-line;">%s</div><br>'%
                                                                            (query.SummonerInfo.encode("utf-8") if query.SummonerInfo else "정보 없음")))
                    self.response.write(htmltools.getContentTitle("<h4>추가된 한줄정보</h4>"))
                    self.response.write(htmltools.getContent(midhtml%(query.SummonerID)))
                    self.response.write('<div class="contentText"><hr><div style="white-space: pre-line;">')
                    data = query.UserComments.encode("utf-8") if query.UserComments else "정보 없음\n"
                    for comment in data.split("\n"):
                        self.response.write("<p>%s</p>"% comment.encode())
                    self.response.write("</div></div>")
                    self.response.write(htmltools.getFooter())
            else:
                self.redirect("../db")
    def post(self):
        # add new summoner
        summonername = self.request.get("SummonerName")
        summonerinfo = self.request.get("SummonerInfo")

        summonerid = generate_random_id() + len(summonername)
        Summoner(SummonerName=summonername, SummonerInfo = summonerinfo,SummonerID=summonerid).put()
        summonerdata = memcache.get("summonerdata")
        dic = OrderedDict()
        summoners = Summoner.query().order(Summoner.SummonerName).fetch(keys_only=True)
        for k in summoners:
            info = k.get()
            dic[info.SummonerName] = info.SummonerID
        if not summonerdata:
            memcache.add("summonerdata", dic)
        else:
            memcache.set("summonerdata", dic)
        self.redirect("../summoner?method=add")



app = webapp2.WSGIApplication([
    ('/summoner', MainPage)

], debug=True)