# -*- coding:utf-8 -*-
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


import os
import webapp2
import random
import time
from google.appengine.ext import ndb
import htmltools
def generate_random_id():
    hashval = random.randint(1, 183532)
    ctime = int(time.time())+hashval
    return ctime
class Summoner(ndb.Model):
    SummonerName = ndb.StringProperty()
    SummonerInfo = ndb.StringProperty()
    SummonerID = ndb.IntegerProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        summonerid = self.request.get("SummonerID")
        if not summonerid:
            self.redirect("../db")
        else:
            query = Summoner.query(Summoner.SummonerID==int(summonerid)).get()
            if query:
                self.response.write(htmltools.getHeader())
                self.response.write(htmltools.getContentTitle("<h2>%s</h2>"%query.SummonerName))
                self.response.write(htmltools.getContent("<p>%s</p>"%query.SummonerInfo.encode("utf-8")))
                self.response.write(htmltools.getFooter())
            else:
                self.redirect("../db")
    def post(self):

        summonername = self.request.get("SummonerName")
        summonerinfo = self.request.get("SummonerInfo")
        summonerid = generate_random_id() + len(summonername)
        Summoner(SummonerName=summonername, SummonerInfo=summonerinfo, SummonerID=summonerid).put()
        self.redirect("../")



app = webapp2.WSGIApplication([
    ('/summoner', MainPage)

], debug=True)