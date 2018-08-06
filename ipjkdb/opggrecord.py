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
from riot_api_tools import opgg_recordGame_gameId, getLiveGameDataBySummonerID, getSummonerByName
#test sheet
#riotapi live game ID:3298536946418
#OPGG button ID      :3298536946
#riotapi live game ID:3298536946418
#OPGG button ID      :3298557917




class MainPage(webapp2.RequestHandler):

    def get(self):
        dx = False
        if not self.request.get("summonername"):
            summonername = "Dashadower"
            summonerdata = getSummonerByName(summonername)
        else:
            dx = True
            summonername = self.request.get("summonername").encode()
            try:
                summonerdata = getSummonerByName(self.request.get("summonername").encode())
            except:
                self.response.write("NO SUCH SUMMONER - " + str(summonername))
                return self.response.set_status(200)
        try:
            gldata = getLiveGameDataBySummonerID(summonerdata["id"])
        except:
            if dx:
                self.response.write("summoner not in game")
        else:
            if dx:
                self.response.write("riotAPI gameID:"+str(gldata["gameId"]) + " length stripped gameID:" + str(gldata["gameId"])[:10])
            if str(gldata["gameQueueConfigId"]) not in ["420", "440"]:
                if dx:
                    self.response.write("NOT RANKED SOLO/FLEX GAME but still attempting to record")

            dt = opgg_recordGame_gameId(str(gldata["gameId"]), summonername)
            if dx:
                self.response.write("response data")
                self.response.write(dt[0])
                self.response.write(dt[1])
            """if dx:
                    self.response.write("OPGG HTTP ERROR - riotAPI gameID:" + str(gldata["gameId"]) + " length stripped gameID:" + str(gldata["gameId"])[:10])
            """

        return self.response.set_status(200)





app = webapp2.WSGIApplication([
    ('/opggrecord', MainPage)

], debug=True)