'''
Created on 2011/11/28

@author: sasaki
'''
import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
#from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
#import json
import OdenkiApiModels

class PostPage(webapp.RequestHandler):
    postedData = {}
    
    def get(self):
        logging.log(logging.DEBUG, "PostPage called")
        self.response.headers['Content-Type'] = "text/html"
        self.response.out.write("<html><head><title>post</title></head><body>")
        self.response.out.write("<p>postid = %s</p>" % OdenkiApiModels.Counter.GetNextId("postid"))
        self.response.out.write("<p>posted data</p><pre>")
        self.response.out.write(cgi.escape(self.request.get('json')))
        self.response.out.write("</pre>")
        self.response.out.write("<p>accepted data</p>")
        self.response.out.write("<table border='1'>")
        for n, v in self.postedData.iteritems():
            self.response.out.write("<tr><td>%s</td><td>%s</td></tr>" % (n, v))
        self.response.out.write("</table>")
        self.response.out.write("</body></html>")

    def post(self):
        parsed_json = json.loads(self.request.get("json"))
        if (parsed_json != None) :
            for n, v in parsed_json.iteritems() :
                self.postedData[n] = v 
        self.get()

application = webapp.WSGIApplication([('/post', PostPage)], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
