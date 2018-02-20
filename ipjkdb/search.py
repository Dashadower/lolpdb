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


import re
from google.appengine.ext import db
import webapp2


class MainPage(webapp2.RequestHandler):

    def post(self):
        template = "(.+?(?=님이 ))"
        pattern = re.compile(template)
        query = self.request.get("query")
        summoners = pattern.findall(query)
        print(summoners)
        self.response.write(str(summoners))




app = webapp2.WSGIApplication([
    ('/search', MainPage)

], debug=True)