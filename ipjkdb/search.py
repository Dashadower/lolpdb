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


from summoner import Summoner
from communitydb import CommunitySummoner
from google.appengine.api import memcache
from collections import OrderedDict
import webapp2


class MainPage(webapp2.RequestHandler):

    def post(self):
        query = self.request.get("query")
        if not query:
            self.redirect("../")
        if query == "Hide on bush":
            self.response.write(
                "<script>alert('소환사 이름: %s\\n 모든 인간들을 패작하고 있습니다');document.location.href='/';</script>" % (
                    query))
        else:
            indb = "등재안됨"
            incdb = "등재안됨"
            cdbhits = 0
            summonerdata = memcache.get("summonerdata")
            result = None
            output = "소환사 이름: %s\\n 도감 등재여부:%s\\n커뮤니티 도감 등재여부: %s\\n커뮤니티 도감 등재 횟수: %d"
            if not summonerdata:
                dic = OrderedDict()
                summoners = Summoner.query().order(Summoner.SummonerName).fetch(keys_only=True)
                for k in summoners:
                    info = k.get()
                    dic[info.SummonerName] = info.SummonerID
                    if info.SummonerName == query.encode():
                        result = info.SummonerID
                memcache.add("summonerdata", dic)
                if result:
                    indb = "등재됨"
            else:
                for key, val in summonerdata.iteritems():
                    if key == query.encode():
                        result = val
                if result:
                    indb = "등재됨"
            commq = CommunitySummoner.query(CommunitySummoner.SummonerName == query.encode()).fetch()
            if commq:
                incdb = "등재됨"
                commq = commq[0]
                cdbhits = commq.SummonerHits
            self.response.write(
                '<script>alert("%s");document.location.href="/";</script>' % (
                output%(query.encode(), indb, incdb, cdbhits)))




app = webapp2.WSGIApplication([
    ('/search', MainPage)

], debug=True)