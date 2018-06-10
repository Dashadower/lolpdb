import webapp2
from google.appengine.api import memcache





class MainPage(webapp2.RequestHandler):

    def get(self):
        memcache.delete("riot")
        memcache.add("riot",0)
        self.response.write("200")


app = webapp2.WSGIApplication([
    ('/resetcache', MainPage)

], debug=True)