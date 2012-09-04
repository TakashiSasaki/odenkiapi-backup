'''
Created on 2011/11/28

@author: sasaki
'''
#import logging
#import cgi
from google.appengine.ext.webapp import WSGIApplication, RequestHandler
from google.appengine.ext.webapp.util import  run_wsgi_app
#from google.appengine.api import users
#from google.appengine.ext.webapp import  template
#from django.utils import  simplejson as json
from model.Sender import GetSender
from model.RawData import putRawData
from model.Data import Data
from model.Metadata import putMetadata
from google.appengine.ext import db

class PostPage(RequestHandler):

    def get(self):
        self.sender = GetSender(self.request)
        self.raw_data = putRawData(self.request)
        #self.data_list = putDataList(self.request)
        self.data_list = Data.storeRequest(self.request)
        self.metadata = putMetadata(self.sender, self.raw_data, self.data_list)
        
        self.response.headers['Content-Type'] = "text/plain"
        for key in self.data_list:
            data = db.get(key)
            self.response.out.write("field:" + data.field + " string:" + data.string + "\n")

    def post(self):
        #logging.info("body="+self.request.body)
        self.get()

if __name__ == "__main__":
    application = WSGIApplication([('/post', PostPage)], debug=True)
    run_wsgi_app(application)
