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

import os
import webapp2
import htmltools
import urllib
from summoner import Summoner
class MainPage(webapp2.RequestHandler):

    def post(self):
        id = self.request.get("SummonerID")
        comment = self.request.get("comment")
        if not id or not comment:
            self.redirect("../db")
        comment = comment.replace("<", "")
        mode = "enable"
        if mode == "disable":
            self.response.write(
                        "<script>alert('일시적으로 해당 기능을 비활성화했습니다.');document.location.href='/summoner?SummonerID=%s';</script>" % (
                            id))
        else:
            query = Summoner.query(Summoner.SummonerID == int(id)).get()
            if query:
                    if query.UserComments:
                        txt = query.UserComments+comment+"\n"
                        query.UserComments = txt
                    else:
                        query.UserComments = (comment+"\n")
                    query.put()
                    self.response.write(
                        "<script>alert('추가했습니다.');document.location.href='/summoner?SummonerID=%s';</script>" % (
                            id))
            else:
                self.redirect("../db")



app = webapp2.WSGIApplication([
    ('/register', MainPage)

], debug=True)