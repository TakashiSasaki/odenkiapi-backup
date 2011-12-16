'''
Created on 2011/11/28

@author: sasaki
'''
import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
#import json
import OdenkiApiModels


class PostPage(webapp.RequestHandler):
    
    def get(self):
        OdenkiApiModels.GetSender(self.request)
        OdenkiApiModels.GetRawData(self.request)
        self.data = {}
        
        self.response.headers['Content-Type'] = "text/html"
        for a in self.request.arguments():
            self.data[a] = self.request.get_all(a)
        
        #self.response.out.write("<html><head><title>post</title></head><body>")
        #self.response.out.write("<p>postid = %s</p>" % OdenkiApiModels.Counter.GetNextId("postid"))
        #self.response.out.write("<p>posted data</p><pre>")
        #self.response.out.write(cgi.escape(self.request.get('json')))
        #self.response.out.write("</pre>")
        #self.response.out.write("<p>accepted data</p>")
        #self.response.out.write("<table border='1'>")
        #for n, v in self.data.iteritems():
        #    self.response.out.write("<tr><td>%s</td><td>%s</td></tr>" % (n, v))
        #self.response.out.write("</table>")
        #self.response.out.write("arguments = %s" % self.request.arguments())
        #self.response.out.write("</body></html>")
        self.write()

    def post(self):
        OdenkiApiModels.GetSender(self.request)
        OdenkiApiModels.GetRawData(self.request)
        self.data = {}

        if self.request.arguments() == []:
            #self.templateValues["body"] = cgi.escape(self.request.body)
            try:
                parsed_json = json.loads(self.request.body)
            except ValueError:
                parsed_json = None
            if (parsed_json != None) :
                for n, v in parsed_json.iteritems() :
                    logging.log(logging.INFO, type(v))
                    if type(v) is list:
                        self.data[n] = v
                    else:
                        self.data[n] = [v]
        self.write()
        
    
    def write(self):
        template_values = {}
        template_values["postid"] = OdenkiApiModels.Counter.GetNextId("postid")
        template_values["arguments"] = self.request.arguments()
        template_values["body"] = cgi.escape(self.request.body)
        template_values["nvlist"] = {}
        for n, v in self.data.iteritems():
            template_values["nvlist"][n] = v
        self.response.out.write(template.render("html/post.html", template_values))        
                

application = webapp.WSGIApplication([('/post', PostPage)], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
