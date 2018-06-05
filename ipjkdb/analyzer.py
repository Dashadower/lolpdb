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
import sys, logging
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
    pmax = ndb.FloatProperty()
    pmin = ndb.FloatProperty()
class AnalysisStats(ndb.Model):
    name = ndb.StringProperty()
    total = ndb.IntegerProperty()
    pj_user = ndb.IntegerProperty()
    pj_potential_user = ndb.IntegerProperty()

def pScoreForChampion(totalgames, wins, kills, assists, deaths):
    winrate_coversion = abs(float(wins)/float(totalgames) - 50.0)
    score_conversion = abs(float(kills + assists)/float(deaths) - 2.25) if deaths else 10.0
    if score_conversion < 1.0:
        score_conversion = 1.0
    return round(winrate_coversion * score_conversion, 3)

##########################
# Constrants for use by the analyzer
ANALYZER_PROJECT_NAME = "2차추적"

TARGET_TIER = ["BRONZE"]

TARGET_DIVISION = ["V"]

##########################

class AnalyzerTaskHandler(webapp2.RequestHandler):
    def post(self):
        summonername = self.request.get("summonername").encode()
        flag = self.request.get("flag")
        summonerdata = riot_api_tools.getSummonerByName(summonername)  # get summoner data from query string

        if summonerdata:  # summoner exists according to riot API
            res = AnalysisData.query(AnalysisData.summonername == summonername).get() # check if summoner exists in DB
            if res:
                found = True
            else:
                found = False
            matches = riot_api_tools.getMatchList(summonerdata["accountId"])  # get a list of last 100 ranked solo games

            if not matches:
                return self.response.set_status(200)  # something went wrong while attempting to fetch games, abort
            elif len(matches) < 20:  # sample size is toooooo small
                if res:
                    res.champdata = {}
                    res.score = 0
                    res.result = "평가불가(이번시즌 내 판수가 20미만)" + str(len(matches))
                    res.put()
                else:
                    res = AnalysisData(summonername=summonername, champdata={}, score=0,
                                       result="평가불가(이번시즌 내 판수가 20미만)" + str(len(matches)))
                    res.put()
                    totalcount = AnalysisStats.query(AnalysisStats.name == ANALYZER_PROJECT_NAME).get()
                    if not totalcount:
                        totalcount = AnalysisStats()
                        totalcount.name = ANALYZER_PROJECT_NAME
                        totalcount.total = AnalysisData.query().count() + 1
                        pj_user = AnalysisData.query(AnalysisData.result == "패작유저").count()
                        pjp_user = AnalysisData.query(AnalysisData.result == "패작 의심유저").count()
                        totalcount.pj_potential_user = pjp_user
                        totalcount.put()
                    else:
                        totalcount.total = totalcount.total + 1
                        totalcount.put()
            else:
                tmp_champstats = {}  # gather info(kills, assists, wins, etc) for each champion
                lastmatch = None  # keep last analyzed match data in case we need to extract teammates
                for match in matches:  # analyze games
                    champid = match["champion"]  # get played champion ID

                    if str(champid) not in tmp_champstats:  # create entity in dict if it doesnt exist
                        tmp_champstats[str(champid)] = {"kills": 0.0, "assists": 0.0, "deaths": 0.0, "score": 0.0,
                                                    "wins": 0.0, "totalgames": 0.0,
                                                    "champname": riot_api_tools.champdata[str(champid)]["name"]}

                    gdata = riot_api_tools.getMatchData(match["gameId"])  # get match game info
                    if not gdata:  # failed fetch: just pass
                        continue
                    lastmatch = gdata
                    data = tmp_champstats[str(champid)]
                    champscore = riot_api_tools.ParseScoreForSummoner(gdata, summonerdata["id"])  # gets (kills, assists, deaths)
                    data["kills"] += float(int(champscore[0]))
                    data["assists"] += float(int(champscore[1]))
                    data["deaths"] += float(int(champscore[2]))
                    data["totalgames"] += 1.0
                    if riot_api_tools.ParseWinrateForSummoner(gdata, summonerdata["id"]):  # check if game won
                        data["wins"] += 1.0

                minscore = 100000000000.0
                maxscore = -100000000000.0
                for key, value in tmp_champstats.iteritems():  # python2: use iteritems
                    if value["totalgames"] >= 10:  #  only calculate champions with more than 10 games played
                        value["score"] = pScoreForChampion(value["totalgames"], value["wins"], value["kills"], value["assists"], value["deaths"])

                        minscore = min(minscore, value["score"])  # get pMax
                        maxscore = max(maxscore, value["score"])  # get pMin

                analysis_result = "실패"
                if minscore == 100000000000.0 or maxscore == -100000000000.0 or minscore == maxscore:  # couldn't get useful data: abort
                    if res:
                        res.champdata = {}
                        res.score = 0
                        res.result = "평가불가(평가가능 챔피언 없음)"
                        res.pmax = maxscore
                        res.pmin = minscore
                        res.put()
                    else:
                        res = AnalysisData(summonername=summonername, champdata={}, score=0,
                                           pmax=maxscore, pmin=minscore,result="평가불가(평가가능 챔피언 없음)")
                        res.put()
                else:

                    user_pscore = maxscore - minscore
                    analysis_result = "평가이전"
                    if user_pscore >= 100.0:  # user is 패작유저
                        analysis_result = "패작유저"
                    elif user_pscore >= 50.0:  # user might be a 패작유저(user is 패작 의심유저)
                        analysis_result = "패작 의심유저"
                    else:
                        analysis_result = "클린유저"

                    if res:  # record summoner analysis data
                        res.champdata = tmp_champstats
                        res.score = user_pscore
                        res.pmax = maxscore
                        res.pmin = minscore
                        res.result = analysis_result
                        res.put()
                    else:
                        res = AnalysisData(summonername=summonername, champdata=tmp_champstats, score=user_pscore,
                                           pmax=maxscore, pmin=minscore,result=analysis_result)
                        res.put()

                # record analysis statistics
                totalcount = AnalysisStats.query(AnalysisStats.name == ANALYZER_PROJECT_NAME).get()
                if not totalcount:
                    totalcount = AnalysisStats()
                    totalcount.name = ANALYZER_PROJECT_NAME
                    if not found:
                        totalcount.total = AnalysisData.query().count() + 1
                    else:
                        totalcount.total = AnalysisData.query().count()
                    pj_user = AnalysisData.query(AnalysisData.result == "패작유저").count()
                    pjp_user = AnalysisData.query(AnalysisData.result == "패작 의심유저").count()
                    if analysis_result == "패작유저":
                        totalcount.pj_user = pj_user + 1
                    else:
                        totalcount.pj_user = pj_user
                    if analysis_result == "패작 의심유저":
                        totalcount.pj_potential_user = pjp_user + 1
                    else:
                        totalcount.pj_potential_user = pjp_user
                    totalcount.put()
                else:
                    if not found:
                        totalcount.total = totalcount.total + 1
                    if analysis_result == "패작유저":
                        totalcount.pj_user = totalcount.pj_user + 1
                    elif analysis_result == "패작 의심유저":
                        totalcount.pj_potential_user = totalcount.pj_potential_user + 1
                    totalcount.put()

                #add next league summoners into analysis queue if flag is true
                if flag == "true":
                    logging.debug("adding next league")
                    leagueinfo = False
                    players = riot_api_tools.ParseTeamsummonerNameByGame(lastmatch, str(summonerdata["id"]))
                    ps = []
                    for teamplayer in players:
                        leagueinfo = riot_api_tools.getLeagueForSummoner(teamplayer[1])
                        if leagueinfo:
                            if leagueinfo[0] in TARGET_TIER and leagueinfo[1] in TARGET_DIVISION:


                                for player in riot_api_tools.ParseSummonersInLeague(leagueinfo[2]):
                                    if player[0] in TARGET_TIER and player[1] in TARGET_DIVISION:
                                        ps.append(player[2])
                    if ps:
                        for g in range(0, len(ps)-1):
                            taskqueue.add(
                                url="/analyzer",
                                target="analyzerservice",
                                queue_name="summoner-analyzer",
                                params={"summonername": ps[g]}
                            )

                        taskqueue.add(
                            url="/analyzer",
                            target="analyzerservice",
                            queue_name="summoner-analyzer",
                            params={"summonername": ps[len(ps)-1],
                                    "flag": "true"}
                        )


















app = webapp2.WSGIApplication([
    ('/analyzer', AnalyzerTaskHandler)

], debug=True)