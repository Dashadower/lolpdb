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
import sys, pickle
reload(sys)
sys.setdefaultencoding("utf-8")
from google.appengine.api import memcache
from analyzer import AnalysisData, AnalysisStats
from htmltools import *
import webapp2
searchform = """
<form method="get" action="../analyzeusers">
    <input type="text" name="summonername", placeholder="소환사 이름">
    <input type="submit" value="찾기">
</form>
"""

class MainPage(webapp2.RequestHandler):

    def get(self):
        if not self.request.get("summonername"):
            self.response.write(getHeader())
            self.response.write(getContentTitle("<h2>2차 브론즈 하위티어 패작러 추적 프로젝트</h2>"))
            #q = AnalysisData.query(AnalysisData.result == "패작유저")
            #trollcount = q.count()
            q = AnalysisStats.query(AnalysisStats.name=="2차추적").get()
            if q:
                total = q.total
                trollcount = q.pj_user
            else:
                total = 0
                trollcount = 0
            self.response.write(getContent("""<h4>패작러 추적 프로젝트 소개</h4><br><p>브론즈 하위티어에 서식중인 패작/양학러들을 찾기 위해 2018년 5월 20일 시작되었습니다. 컴퓨터가 브론즈 하위티이어에 
                                           있는 소환사들을 무작위로 선택하여 전적을 분석한후 패작유저, 패작의심유저, 클린유저로 자동 분류합니다.</p>
                                           
                                           <h3>2차 추적 프로젝트</h3>
                                           <p>2차 추적 프로젝트는 6월 6일 오전 1시부터 6월 30일 까지 계속될 계획이며, 목표 분석량은 브론즈 5 전체 인구입니다.
                                           현재까지 소환사 <b>%d</b>명이 분석되었으며, 이중 <b>%d</b>명(총 분석인원의 %.2f%%)이 패작러로 분석되었습니다. 물론 자동으로 분석되기에 패작러가 아니지만 패작유저로 분석되고, 패작유저지만 클린유저로
                                           분석되는 등의 오류는 충분히 발생할수 있습니다.<br>
                                           1차에 비해 패작러 분석방법의 정확도를 훨씬 개선하였고, 분석 범위도 브론즈 5를 벗어나지 않게 보완했습니다.</p>
                                           <hr>
                                           <br><h4>2018.6.6 수정</h4><h3>1차 예비조사가 끝났습니다!</h3>
                                           <br>
                                           <p>5월 20일부터 6월 6일 자정까지 시행된 1차 패작러 조사는 일종의 시범 시행이었습니다. 
                                           처음 시행 당시 패작러와 일반유저를 잘 구분하지 못했고, 티어 분포도 원래 목적인 브론즈 5에서 크게 벗어났습니다.
                                           그럼에도 불구하고 15일간 소환사 <b>125710</b>명의 전적을 분석하였고, 이중 <b>617</b>명이 패작러로 판별되었습니다.</p>
                                           """%(total, trollcount, (float(trollcount)/float(total))*100)))
            self.response.write(getContent(searchform+"<hr>"))
            self.response.write(getContentTitle("패작러로 분석된 소환사들"))

            self.response.write(getContent("<h5>총 %d명</h5>"%(trollcount)))
            self.response.write(getContent("<p>무작위 패작러 10명</p>"))
            q = AnalysisData.query(AnalysisData.result == "패작유저")
            dt = q.fetch(10)
            if dt:
                for pj in dt:
                    self.response.write(getContent("""<a href="../analyzeusers?summonername=%s">%s</a>"""%(pj.summonername, pj.summonername)))
            self.response.write(getFooter())
        else:
            summonername = self.request.get("summonername").encode()
            dt = AnalysisData.query(AnalysisData.summonername==summonername).get()
            if not dt:
                self.response.write("<script>alert('소환사 이름: %s\\n아직 분석되지 않았습니다');document.location.href='/analyzeusers';</script>" % (summonername))
            else:
                self.response.write(getHeader())
                self.response.write(getContent("<h2>%s</h2>"%dt.summonername))
                self.response.write(getContent("<p>패작점수:%.1f</p>"%(dt.score)))
                self.response.write(getContent("""<button onclick="document.location.href='http://www.op.gg/summoner/userName=%s'">OP.GG</button>"""%(summonername)))
                self.response.write(getContent("<br><h6>세부 챔피언 정보</h6>"))
                self.response.write(getContent("<table><tr><th>챔피언</th><th>판수</th><th>평점(0.0은 Perfect)</th><th>승률</th></tr>"))
                for key, value in dt.champdata.iteritems():
                    self.response.write(getContent("<tr><td>%s</td><td>%d</td><td>%.1f</td><td>%.1f</td></tr>"%(value["champname"],value["totalgames"],value["score"],(value["wins"]/value["totalgames"])*100)))
                self.response.write(getContent("</table>"))
                self.response.write(getContent("<p>pMax:%.3f pMin:%.3f</p>"%(dt.pmax if dt.pmax else 0.0, dt.pmin if dt.pmin else 0.0)))
                self.response.write(getContent("<br><h3>분석결과:%s</h3>"%(dt.result)))
                self.response.write(getFooter())






app = webapp2.WSGIApplication([
    ('/analyzeusers', MainPage)

], debug=True)