#import logging
#from MyRequestHandler import MyRequestHandler
#from google.appengine.api import memcache
from google.appengine.ext.webapp import RequestHandler, WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
#import cgi
#import simplejson
#import lib
from model.RawDataNdb import RawData
from google.appengine.ext import ndb

#DEFAULT_LIMIT = 100

#from google.appengine.ext import ndb

class RawDataStartEnd(RequestHandler):
    @ndb.toplevel
    def get(self):
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])
        raw_data_keys = RawData.getRecentKeys(start, end)
        for raw_data_key in raw_data_keys:
            self.response.out.write(str(raw_data_key.get()))

if __name__ == "__main__":
    #logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/record/RawData/[0-9]+/[0-9]+', RawDataStartEnd), ], debug=True)
    run_wsgi_app(application)
