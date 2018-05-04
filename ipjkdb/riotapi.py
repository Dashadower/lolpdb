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


import logging
import time
from datetime import datetime, timedelta
import webapp2
from urllib import urlopen, quote
import json
from summoner import Summoner
api_key = "RGAPI-eadde91c-c083-4d83-8d4e-e15d3b524a10"
get_riot_id = "https://kr.api.riotgames.com/lol/summoner/v3/summoners/by-name/%s?api_key=%s"
get_league_info = "https://kr.api.riotgames.com/lol/league/v3/positions/by-summoner/%s?api_key=%s"
class MainPage(webapp2.RequestHandler):

    def get(self):
        if not self.request.get("summonerid"):
            self.redirect("../db")
        else:
            summonerid = self.request.get("summonerid")
            query = Summoner.query(Summoner.SummonerID == int(summonerid)).get()
            if query.APIUpdateTime_int:
                if int(time.time()) - query.APIUpdateTime_int < 180:
                    self.response.write('<script>alert("최근에 정보를 갱신했습니다");document.location.href="/summoner?SummonerID=%s";</script>'%(summonerid))

            if query.RiotID:
                riotid = query.RiotID
                apidata = json.loads(urlopen(get_league_info % (riotid, api_key)).read())
                tierinfo = " ".join([apidata[0]["tier"], apidata[0]["rank"], str(apidata[0]["leaguePoints"]) + " LP"])
                totalgames = (apidata[0]["wins"] + apidata[0]["losses"])
                winrate = int(float(apidata[0]["wins"]) / float(totalgames) * 100)
                ctime = int(time.time())
                dt = datetime.fromtimestamp(time.mktime(time.localtime()))
                dt = dt - timedelta(hours=3)
                friendlytime = "%d:%s:%s" % (dt.hour, str(dt.minute).rjust(2, "0"), str(dt.second).rjust(2, "0"))
                query.SummonerTier = tierinfo
                query.SummonerWinRate = winrate
                query.SummonerGameInfo = "%d전 %d승 %d패" % (
                (apidata[0]["wins"] + apidata[0]["losses"]), apidata[0]["wins"], apidata[0]["losses"])
                query.APIUpdateTime = friendlytime
                query.APIUpdateTime_int = ctime
                query.put()
                self.response.write(
                    '<script>alert("정보를 갱신했습니다");document.location.href="/summoner?SummonerID=%s";</script>' % (
                        summonerid))
            else:
                try:
                    riotid = str(json.loads(urlopen(get_riot_id%(quote(query.SummonerName.encode()), api_key)).read())["id"])

                    if not riotid:
                        self.response.write(
                            '<script>alert("정보를 갱신할수 없습니다(해당 소환사가 존재하지 않습니다)");document.location.href="/summoner?SummonerID=%s";</script>' % (
                                summonerid))
                except:
                    self.response.write(
                        '<script>alert("정보를 갱신할수 없습니다(해당 소환사가 존재하지 않습니다)");document.location.href="/summoner?SummonerID=%s";</script>' % (
                            summonerid))
                else:
                    apidata = json.loads(urlopen(get_league_info % (riotid, api_key)).read())
                    tierinfo = " ".join(
                        [apidata[0]["tier"], apidata[0]["rank"], str(apidata[0]["leaguePoints"]) + " LP"])
                    totalgames = (apidata[0]["wins"] + apidata[0]["losses"])
                    winrate = int(float(apidata[0]["wins"]) / float(totalgames) * 100)
                    ctime = int(time.time())
                    dt = datetime.fromtimestamp(time.mktime(time.localtime()))
                    dt = dt - timedelta(hours=3)
                    friendlytime = "%d:%s:%s" % (dt.hour, str(dt.minute).rjust(2, "0"), str(dt.second).rjust(2, "0"))
                    query.SummonerTier = tierinfo
                    query.SummonerWinRate = winrate
                    query.SummonerGameInfo = "%d전 %d승 %d패" % (
                    (apidata[0]["wins"] + apidata[0]["losses"]), apidata[0]["wins"], apidata[0]["losses"])
                    query.APIUpdateTime = friendlytime
                    query.APIUpdateTime_int = ctime
                    query.put()
                    self.response.write(
                        '<script>alert("정보를 갱신했습니다");document.location.href="/summoner?SummonerID=%s";</script>' % (
                            summonerid))





app = webapp2.WSGIApplication([
    ('/riotapi', MainPage)

], debug=True)