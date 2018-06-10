import webapp2
from google.appengine.api import memcache
#T his script is used by admin.py by calling ajax request to this handler, to see how many Riot API requests has been
# made within a minute




class MainPage(webapp2.RequestHandler):

    def get(self):
        data = memcache.get("riot")
        if data != None:
            self.response.write(str(data)+" calls")
        elif data == None:
            self.response.write("No data available(check memcache)")


app = webapp2.WSGIApplication([
    ('/getapicount', MainPage)

], debug=True)