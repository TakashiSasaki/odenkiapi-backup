'''
Created on 2011/11/28

@author: sasaki
'''
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
#from MyRequestHandler import MyRequestHandler
from lib.CachedContent import CachedContent
from google.appengine.ext.webapp import RequestHandler

class MainPage(RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        #self.response.out.write('Hello, webapp World!')
        current_user = users.GetCurrentUser()
        
        cached_content = CachedContent("/", {}, "html/index.html")
        cached_content.render()
        cached_content.write(self)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/', MainPage)], debug=True)
    run_wsgi_app(application)
