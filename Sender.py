import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
#import json
import OdenkiApiModels


class SenderRequestHandler(webapp.RequestHandler):
    
    def get(self):
        senders = OdenkiApiModels.Sender.all()
        template_values = {}
        template_values["senders"] = []
        for sender in senders:
            template_values["senders"].append(
                                           {"senderId": sender.senderId,
                                            "protocol":sender.protocol,
                                            "ipAddress": sender.ipAddress,
                                            "port":sender.port})
        
        self.response.out.write(template.render("html/Sender.html", template_values))


application = webapp.WSGIApplication([('/Sender', SenderRequestHandler)], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
