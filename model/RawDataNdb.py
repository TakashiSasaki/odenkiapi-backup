#import lib
#from urlparse import urlparse
from google.appengine.ext import ndb
#from google.appengine.ext.webapp import Request
from model.Counter import Counter
from json import dumps
from logging import debug
from model.NdbModel import NdbModel
#ctx = ndb.get_context()
#lib.debug("ndb cache policy is %s" % ctx.get_cache_policy())
#lib.debug("ndb memcache policy is %s" % ctx.get_memcache_policy())
#lib.debug("ndb memcache timeout is %s" % ctx.get_memcache_timeout_policy())
#ctx.set_memcache_policy(True)
#ctx.set_cache_policy(True)
#ctx.set_memcache_timeout_policy(7200)

class RawData(NdbModel):
    rawDataId = ndb.IntegerProperty()
    path = ndb.StringProperty(indexed=False)
    parameters = ndb.StringProperty(indexed=False)
    query = ndb.StringProperty(indexed=False)
    fragment = ndb.StringProperty(indexed=False)
    body = ndb.StringProperty(indexed=False)
    #_use_cache = True
    #_use_memcache = True
    #_memcache_timeout = 7200

    fieldnames = ["rawDataId", "path", "parameters", "query", "fragment", "body"]
    
    @classmethod
    def queryRange(cls, start, end):
        debug("getRecentRawData start=%s end=%s" % (start, end))
        q = ndb.Query(kind="RawData")
        if start < end:
            q = q.order(cls.rawDataId)
            q = q.filter(cls.rawDataId>=start)
            q = q.filter(cls.rawDataId<=end)
            return q
        else:
            q = q.order(-cls.rawDataId)
            q = q.filter(cls.rawDataId<=start)
            q = q.filter(cls.rawDataId>=end)
            return q
    
    @classmethod
    def queryRecent(cls):
        """returns iterator which yields ndb.Key object"""
        query = ndb.Query(kind="RawData")
        query = query.order(-cls.rawDataId)
        return query

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

    def toDict(self):
        return self.to_dict()
    
    def toJson(self):
        return dumps(self.to_dict()) 
