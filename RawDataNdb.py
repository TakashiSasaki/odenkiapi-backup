import logging
from MyRequestHandler import MyRequestHandler
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import RequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
import cgi
import simplejson
import lib

DEFAULT_LIMIT = 100

from google.appengine.ext import ndb

class RawData(ndb.Model):
    rawDataId = ndb.IntegerProperty()
    path = ndb.StringProperty(indexed=False)
    parameters = ndb.StringProperty(indexed=False)
    query = ndb.StringProperty(indexed=False)
    fragment = ndb.StringProperty(indexed=False)
    body = ndb.StringProperty(indexed=False)
    
    @classmethod
    def getRecentRawData(cls, start, end):
        lib.debug("getRecentRawData start=%s end=%s" % (start,end))
        q = ndb.Query(kind="RawData")
        if start < end:
            q = q.order(cls.rawDataId)
            limit = end - start + 1
        else:
            q = q.order(-cls.rawDataId)
            limit = start - end + 1
        entities = q.fetch(limit)
        lib.debug("%s entities were fetched" % len(entities))
        return entities

class RawDataStartEnd(RequestHandler):
    def get(self):
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])
        raw_data = RawData.getRecentRawData(start, end)
        for x in raw_data:
            self.response.out.write(str(x))

class RawDataNdbRequestHandler(MyRequestHandler):
    
    def get(self):
        limit = self.request.get("limit")
        if limit is None or len(limit)==0:
            limit = DEFAULT_LIMIT
        else:
            try:
                limit = int(limit[0])
            except Exception:
                limit = DEFAULT_LIMIT
        assert isinstance(limit, int)

        query_recent = RawData.queryRecent(limit = limit);
        results = []
        for raw_data in query_recent:
            query_dict = cgi.parse_qs(raw_data.query)
            if query_dict.has_key("arduinoid"):
                gen_power = query_dict["gen.power(W)"][0]
                timestring = query_dict["time"][0]
                results.append([gen_power, timestring[0:4], timestring[4:6], timestring[6:8], timestring[8:10], timestring[10:12], timestring[12:14]])
        
        self.response.out.write(self.request.get("callback") + "(" + simplejson.dumps({"timeVsWatt":results}) + ");")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/resource/RawData/[0-9]+/[0-9]+', RawDataStartEnd), ], debug=True)
    run_wsgi_app(application)
