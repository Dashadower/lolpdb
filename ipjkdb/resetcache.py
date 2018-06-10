import webapp2
from google.appengine.api import memcache





class MainPage(webapp2.RequestHandler):

    def get(self):
        summonerdata = memcache.get("riot")
        if not summonerdata:
            pass
        else:
            memcache.set("riot", 0)
        self.response.write("200")


app = webapp2.WSGIApplication([
    ('/resetcache', MainPage)