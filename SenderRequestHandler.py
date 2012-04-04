import logging
import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
from google.appengine.ext.webapp import  template
from django.utils import  simplejson as json
#import json
from Sender import Sender
from MyRequestHandler import MyRequestHandler

class SenderRequestHandler(MyRequestHandler):
    
    def get(self):
        gql = Sender.gql("ORDER BY senderId DESC")
        #senders = Sender.all()
        senders = gql.run()
        template_values = {}
        template_values["senders"] = []
        for sender in senders:
            template_values["senders"].append(
                                           {"senderId": sender.senderId,
                                            "protocol":sender.protocol,
                                            "ipAddress": sender.ipAddress,
                                            "port":sender.port})
            logging.info(template_values)
        self.writeWithTemplate(template_values, "Sender")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/Sender', SenderRequestHandler)], debug=True)
    run_wsgi_app(application)
