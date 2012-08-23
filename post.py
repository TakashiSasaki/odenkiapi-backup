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
from Sender import GetSender
from RawData import putRawData
from Data import putDataList
from Metadata import putMetadata
from google.appengine.ext import db

class PostPage(webapp.RequestHandler):

    def get(self):
        self.sender = GetSender(self.request)
        self.raw_data = putRawData(self.request)
        self.data_list = putDataList(self.request)
        self.metadata = putMetadata(self.sender, self.raw_data, self.data_list)
        
        self.response.headers['Content-Type'] = "text/plain"
        for key in self.data_list:
            data = db.get(key)
            self.response.out.write("field:" + data.field + " string:" + data.string + "\n")

    def post(self):
        #logging.info("body="+self.request.body)
        self.get()

application = webapp.WSGIApplication([('/post', PostPage)], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
