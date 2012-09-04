#import logging
from urlparse import urlparse
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.ext.webapp import Request
from model.Counter import Counter
import lib

class RawData(db.Model):
    rawDataId = db.IntegerProperty()
    path = db.StringProperty(indexed=False)
    parameters = db.StringProperty(indexed=False)
    query = db.StringProperty(indexed=False)
    fragment = db.StringProperty(indexed=False)
    body = db.StringProperty(indexed=False)
    
def putRawData(request):
    assert isinstance(request, Request)
    parsed_url = urlparse(request.url)
    path = parsed_url.path
    parameters = parsed_url.params
    query = parsed_url.query
    fragment = parsed_url.fragment
    body = request.body
    raw_data = RawData()
    raw_data.rawDataId = Counter.GetNextId("rawDataId")
    raw_data.path = path
    raw_data.parameters = parameters
    raw_data.query = query
    raw_data.fragment = fragment
    raw_data.body = body
    return raw_data.put()

class RawDataNdb(ndb.Model):
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
