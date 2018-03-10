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
from summoner import Summoner
from collections import OrderedDict




class MainPage(webapp2.RequestHandler):

    def get(self):
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
        self.response.write("200")



app = webapp2.WSGIApplication([
    ('/updatecache', MainPage)

], debug=True)
