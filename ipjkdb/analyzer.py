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
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import taskqueue
import riot_api_tools

class AnalysisData(ndb.Model):
    summonername = ndb.StringProperty()
    champdata = ndb.PickleProperty()
    score = ndb.FloatProperty()
    result = ndb.StringProperty()
class AnalysisStats(ndb.Model):
    name = ndb.StringProperty()
    total = ndb.IntegerProperty()
    pj_user = ndb.IntegerProperty()
    pj_potential_user = ndb.IntegerProperty()
class AnalyzerTaskHandler(webapp2.RequestHandler):
    def post(self):
        summonername = self.request.get("summonername").encode()
        summonerdata = riot_api_tools.getSummonerByName(summonername)
        if summonerdata:
            matches = riot_api_tools.getMatchList(summonerdata["accountId"])
            if not matches:
                return self.response.set_status(200)
            elif len(matches) <= 10:
                res = AnalysisData.query(AnalysisData.summonername==summonername).get()
                if res:
                    res.champdata = {}
                    res.score = 0
                    res.result = "평가불가(이번시즌 내 판수가 10미만)"+str(len(matches))
                    res.put()
                else:
                    res = AnalysisData(summonername=summonername, champdata={}, score=0, result="평가불가(이번시즌 내 판수가 10미만"+str(len(matches)))
                    res.put()
            else:
                _champdata = {} # "str(champid)": {kills,assists,deaths,wins.totalgames,champname}
                nextmatch = None
                for match in matches:
                    champid = match["champion"]
                    if str(champid) not in _champdata:
                        _champdata[str(champid)] = {"kills":0.0,"assists":0.0,"deaths":0.0,"score":0.0,"wins":0.0,"totalgames":0.0,"champname":riot_api_tools.champdata[str(champid)]["name"]}
                    gdata = riot_api_tools.getMatchData(match["gameId"])
                    if not gdata:
                        continue
                    data = _champdata[str(champid)]
                    champscore = riot_api_tools.ParseScoreForSummoner(gdata, summonerdata["id"])
                    data["kills"] += float(int(champscore[0]))
                    data["assists"] += float(int(champscore[1]))
                    data["deaths"] += float(int(champscore[2]))
                    data["totalgames"] += 1.0
                    if riot_api_tools.ParseWinrateForSummoner(gdata, summonerdata["id"]):
                        data["wins"] += 1.0
                    nextmatch = gdata
                for key, value in _champdata.iteritems():
                    value["score"] = round((value["kills"] + value["assists"]) / value["deaths"], 1) if value["deaths"] != 0 else 10
                score = 0.0
                numberofchamps = 0.0
                for key, value in _champdata.iteritems():
                    if value["totalgames"] >= 5.0:

                        winrate = round(value["wins"]/value["totalgames"],1)
                        score += abs(winrate - 50.0) * winrate * 1.5
                        score += abs(value["score"] - 2.0) * value["score"] * 10
                        numberofchamps += 1
                if numberofchamps != 0:
                    score = round(score/numberofchamps,1)
                elif numberofchamps == 0:
                    score = 0
                res = AnalysisData.query(AnalysisData.summonername==summonername).get()
                if score >= 220.0:
                    sys = "패작유저"
                elif score >= 150.0:
                    sys = "패작 의심유저"
                else:
                    sys = "클린유저"
                if res:
                    res.champdata = _champdata
                    res.score = score
                    res.result = sys
                    res.put()
                else:
                    res = AnalysisData(summonername=summonername, champdata=_champdata,score=score,result=sys)
                    res.put()
                if nextmatch:
                    idx = 0
                    for team in riot_api_tools.ParseTeamsummonerNameByGame(nextmatch, str(summonerdata["id"])):
                        if idx <= 2:
                            taskqueue.add(
                                url="/analyzer",
                                target="analyzerservice",
                                queue_name="summoner-analyzer",
                                params={"summonername": team}
                            )
                            idx += 1
                totalcount = AnalysisStats.query(AnalysisStats.name=="1차추적").get()
                if not totalcount:
                    totalcount = AnalysisStats()
                    totalcount.total = AnalysisData.query().count() + 1
                    pj_user = AnalysisData.query(AnalysisData.result == "패작유저").count()
                    pjp_user = AnalysisData.query(AnalysisData.result == "패작 의심유저").count()
                    if sys == "패작유저":
                        totalcount.pj_user = pj_user + 1
                    else:
                        totalcount.pj_user = pj_user
                    if sys == "패작 의심유저":
                        totalcount.pj_potential_user = pjp_user + 1
                    else:
                        totalcount.pj_potential_user = pjp_user
                    totalcount.put()
                else:
                    totalcount.total = totalcount.total + 1
                    if sys == "패작유저":
                        totalcount.pj_user = totalcount.pj_user + 1
                    elif sys == "패작 의심유저":
                        totalcount.pj_potential_user = totalcount.pj_potential_user + 1
                    totalcount.put()













app = webapp2.WSGIApplication([
    ('/analyzer', AnalyzerTaskHandler)

], debug=True)