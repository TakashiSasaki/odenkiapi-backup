from __future__ import unicode_literals, print_function
from google.appengine.ext import ndb
#from google.appengine.ext.webapp import Request
from model.Counter import Counter
#from json import dumps
from logging import debug
from model.NdbModel import NdbModel

class RawData(NdbModel):
    rawDataId = ndb.IntegerProperty()
    path = ndb.StringProperty(indexed=False)
    parameters = ndb.StringProperty(indexed=False)
    query = ndb.StringProperty(indexed=False)
    fragment = ndb.StringProperty(indexed=False)
    body = ndb.StringProperty(indexed=False)

    fieldnames = ["rawDataId", "path", "parameters", "query", "fragment", "body"]
    
    def to_list(self):
        return [self.rawDataId, self.path, self.parameters, self.query, self.fragment, self.body]
    
    @classmethod
    def queryRange(cls, start, end):
        debug("getRecentRawData start=%s end=%s" % (start, end))
        q = ndb.Query(kind="RawData")
        if start < end:
            q = q.order(cls.rawDataId)
            q = q.filter(cls.rawDataId >= start)
            q = q.filter(cls.rawDataId <= end)
            return q
        else:
            q = q.order(-cls.rawDataId)
            q = q.filter(cls.rawDataId <= start)
            q = q.filter(cls.rawDataId >= end)
            return q
    
    @classmethod
    def fetchRange(cls, start, end, limit=100):
        return cls.queryRange(start, end).fetch(keys_only=True, limit=100)
    
    @classmethod
    def queryRecent(cls):
        """returns iterator which yields ndb.Key object"""
        query = ndb.Query(kind="RawData")
        query = query.order(-cls.rawDataId)
        return query
    
    @classmethod
    def fetchRecent(cls, limit=100):
        return cls.queryRecent().fetch(keys_only=True, limit=limit)

    @classmethod
    def queryPeriod(cls, start_rawdata_id, end_rawdata_id):
        assert isinstance(start_rawdata_id, int)
        assert isinstance(end_rawdata_id, int)
        q = ndb.Query(kind="RawData")
        if start_rawdata_id >= end_rawdata_id:
            q = q.order(-cls.rawDataId)
            q = q.filter(cls.rawDataId <= start_rawdata_id)
            q = q.filter(cls.rawDataId >= end_rawdata_id)
        else:
            q = q.order(-cls.rawDataId)
            q = q.filter(cls.rawDataId <= end_rawdata_id)
            q = q.filter(cls.rawDataId >= start_rawdata_id)
        return q

    #def toDict(self):
    #    return self.to_dict()
    
    #def toJson(self):
    #    return dumps(self.to_dict())
     
