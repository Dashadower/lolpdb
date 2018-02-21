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


from google.appengine.ext import db
from google.appengine.api import memcache
import webapp2


class MainPage(webapp2.RequestHandler):

    def post(self):

        query = self.request.get("query")
        if not query:
            self.redirect("../")

        summonerdata = memcache.get("summonerdata")
        result = None
        if not summonerdata:
            dic = OrderedDict()
            summoners = Summoner.query().order(Summoner.SummonerName).fetch(keys_only=True)
            for k in summoners:
                info = k.get()
                dic[info.SummonerName] = info.SummonerID
                if info.SummonerName == query.encode():
                    result = info.SummonerID
            memcache.add("summonerdata", dic)
            if not result:
                self.response.write("<script>alert('해당 소환사는 도감에 등록되어있지 않습니다');document.location.href='/';</script>")

            else:
                self.redirect("../summoner?SummonerID=%d"%result)
        else:
            for key, val in summonerdata.iteritems():
                if key == query.encode():
                    result = val
            if result:
                self.redirect("../summoner?SummonerID=%d" % result)
            else:
                self.response.write("<script>alert('해당 소환사는 도감에 등록되어있지 않습니다');document.location.href='/';</script>")





app = webapp2.WSGIApplication([
    ('/search', MainPage)

], debug=True)