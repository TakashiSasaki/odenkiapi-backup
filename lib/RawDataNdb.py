import lib
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
