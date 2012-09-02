import logging
from MyRequestHandler import MyRequestHandler
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import cgi
import simplejson

DEFAULT_LIMIT = 100

from google.appengine.ext import ndb

class RawData(ndb.Model):
    rawDataId = ndb.IntegerProperty()
    path = ndb.StringProperty()
    parameters = ndb.StringProperty()
    query = ndb.StringProperty()
    fragment = ndb.StringProperty()
    body = ndb.StringProperty()
    
    @classmethod
    def queryRecent(cls, limit):
        q = cls.query(limit=limit)
        q = q.order(-cls.rawDataId)
        return q

class RawDataNdb(MyRequestHandler):
    
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
    application = webapp.WSGIApplication([('/RawDataNdb', RawDataNdb) ], debug=True)
    run_wsgi_app(application)
