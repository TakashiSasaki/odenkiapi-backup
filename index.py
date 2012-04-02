'''
Created on 2011/11/28

@author: sasaki
'''
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os

class MainPage(webapp.RequestHandler):
    
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        #self.response.out.write('Hello, webapp World!')
        current_user = users.GetCurrentUser()
        template_values = {"version": os.environ['CURRENT_VERSION_ID']}
        self.response.out.write(template.render("html/index.html", template_values))        


application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
