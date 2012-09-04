import lib
from google.appengine.ext import ndb

#ctx = ndb.get_context()
#lib.debug("ndb cache policy is %s" % ctx.get_cache_policy())
#lib.debug("ndb memcache policy is %s" % ctx.get_memcache_policy())
#lib.debug("ndb memcache timeout is %s" % ctx.get_memcache_timeout_policy())
#ctx.set_memcache_policy(True)
#ctx.set_cache_policy(True)
#ctx.set_memcache_timeout_policy(7200)

class RawData(ndb.Model):
    rawDataId = ndb.IntegerProperty()
    path = ndb.StringProperty(indexed=False)
    parameters = ndb.StringProperty(indexed=False)
    query = ndb.StringProperty(indexed=False)
    fragment = ndb.StringProperty(indexed=False)
    body = ndb.StringProperty(indexed=False)
    #_use_cache = True
    #_use_memcache = True
    #_memcache_timeout = 7200
    
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
        entities = q.fetch(limit, keys_only=True)
        lib.debug("%s entities were fetched" % len(entities))
        return entities

