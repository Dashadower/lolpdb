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
from google.appengine.api import taskqueue, memcache
html = """
<html>
<title>admin control</title>
<body>
    <form action="/admin" method="get">
        소환사 이름:<br>
        <input type="text" name="summonername">
        <br>
        flag:<br>
        <input type="radio" name="flag" value="false" checked> false<br>
        <input type="radio" name="flag" value="true"> true<br>
        <br><br>
        <input type="hidden" name="method" value="task">
        <input type="submit" value="Submit">
    </form> 
<br><br>
<h3>summoner-analyzer queue stats</h3>
"""
endhtml = """
</body>
</html>
"""

class MainPage(webapp2.RequestHandler):

    def get(self):
        if self.request.get("method") == "task" and self.request.get("summonername"):
            if self.request.get("flag"):
                sname = self.request.get("summonername").encode()
                taskqueue.add(
                    url="/analyzer",
                    target="analyzerservice",
                    queue_name="summoner-analyzer",
                    params={"summonername": sname,
                            "flag":"true"}
                )
            else:
                sname = self.request.get("summonername").encode()
                taskqueue.add(
                    url = "/analyzer",
                    target = "analyzerservice",
                    queue_name = "summoner-analyzer",
                    params={"summonername": sname}
                )
            self.response.write("%s has been added to analyzer_service"%(self.request.get("summonername")))
        else:
            statsList = taskqueue.QueueStatistics.fetch(taskqueue.Queue("summoner-analyzer"))
            self.response.write(html)
            self.response.write(str(statsList))
            apistats = memcache.get(key="riot")
            if apistats:
                self.response.write("API calls in the last minute: %d"%(apistats))

            self.response.write(endhtml)






app = webapp2.WSGIApplication([
    ('/admin', MainPage)
], debug=True)