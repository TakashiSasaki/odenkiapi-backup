from __future__ import unicode_literals
from logging import debug
from warnings import warn
from google.appengine.ext import ndb
from google.appengine.ext.webapp import Request
#import types,logging
from model.Counter import Counter
#from django.utils import simplejson
from json import loads
from model.NdbModel import NdbModel
from google.appengine.api.memcache import Client

class Data(NdbModel):
    dataId = ndb.IntegerProperty()
    field = ndb.StringProperty()
    string = ndb.StringProperty()
    
    fieldnames = ["dataId", "field", "string"]
    
    def to_list(self):
        return [self.dataId, self.field, self.string]
    
    @classmethod
    def queryByField(cls, field):
        query = ndb.Query(kind="Data")
        query = query.order(cls.dataId)
        query = query.filter(cls.field == field)
        return query

    @classmethod
    def fetchByField(cls, field):
        return cls.queryByField(field).fetch(limit=100, keys_only=True)
    
    @classmethod
    def queryByFieldAndString(cls, field, string):
        assert isinstance(field, unicode)
        assert isinstance(string, unicode)
        query = ndb.Query(kind="Data")
        query = query.order(cls.dataId)
        query = query.filter(cls.field == field)
        query = query.filter(cls.string == string)
        return query

    @classmethod
    def fetchByFieldAndString(cls, field, string):
        assert isinstance(field, unicode)
        assert isinstance(string, unicode)
        MEMCACHE_KEY = "kml87wngfp98uw45nvljkbbjlkq4" + field + string
        client = Client()
        data_keys = client.get(MEMCACHE_KEY)
        if data_keys is None: return []
        data_keys = cls.queryByFieldAndString(field, string).fetch(keys_only=True)
        if len(data_keys) >= 2: warn("duplicated data entities with field=%s and string=%s" % (field, string))
        client.set(MEMCACHE_KEY, data_keys)
        return data_keys
    
    @classmethod
    def querySingle(cls, data_id):
        warn("querySingle is deprecatd. Use getByDataId instead.", DeprecationWarning, 2)
        query = ndb.Query(kind="Data")
        query = query.filter(Data.dataId == data_id)
        return query
    
    @classmethod
    def getByDataId(cls, data_id):
        assert isinstance(data_id, int)
        query = ndb.Query(kind="Data")
        query = query.filter(cls.dataId == data_id)
        return query.get(keys_only=True)
    
    @classmethod
    def queryRecent(cls):
        query = ndb.Query(kind="Data")
        query = query.order(-Data.dataId)
        return query
    
    @classmethod
    def queryByDataId(cls, data_id):
        assert isinstance(data_id, int)
        query = ndb.Query(kind="Data")
        query = query.filter(cls.dataId == data_id)
        return query

    
    @classmethod
    def queryRange(cls, start, end):
        assert isinstance(start, int)
        assert isinstance(end, int)
        query = ndb.Query(kind="Data")
        if start <= end:
            query = query.filter(cls.dataId >= start)
            query = query.filter(cls.dataId <= end)
            return query
        else:
            query = query.order(-cls.dataId)
            query = query.filter(cls.dataId <= start)
            query = query.filter(cls.dataId >= end)
            return query
    
    def queryDuplication(self):
        query = ndb.Query(kind="Data")
        query = query.filter(Data.field == self.field)
        query = query.filter(Data.string == self.string)
        query = query.order(Data.dataId)
        return query

    @classmethod
    def putEntity(cls, field, string):
        debug("type of field is %s" % type(field))
        field = unicode(field)
        assert isinstance(field, unicode)
        string = unicode(string)
        assert isinstance(string, unicode)
        q = cls.getByFieldAndString(field, string)
        k = q.get(keys_only=True)
        if k: return k

        data = cls()
        assert isinstance(data, ndb.Model)
        data.dataId = Counter.GetNextId("dataId")
        data.field = field
        data.string = string
        data.put()
        q = cls.getByFieldAndString(field, string)
        k = q.get(keys_only=True)
        return k
        
    @classmethod
    def putParams(cls, query_string):
        from urlparse import parse_qs
        d = parse_qs(query_string)
        assert isinstance(d, dict)
        l = []
        for key_in_dict in d.keys():
            for value_in_dict in d.get(key_in_dict):
                if isinstance(value_in_dict, list):
                    for item in value_in_dict:
                        assert isinstance(item, unicode)
                        entity_key = cls.putEntity(key_in_dict, item)
                        if entity_key not in l:
                            l.append(entity_key)
                else:
                    entity_key = cls.putEntity(key_in_dict, value_in_dict)
                    l.append(entity_key)
        return l
    
    @classmethod
    def putRequest(cls, request):
        assert isinstance(request, Request)
        data_list = []
        for field in request.arguments():
            vlist = request.get_all(field)
            #logging.info((k,vlist))
            assert isinstance(vlist, list)
            for string in vlist:
                data = cls.putEntity(field, string)
                if data is None: continue
                data_list.append(data)
        try:
            parsed_json = loads(request.body)
        except ValueError:
            parsed_json = None
    
        if (parsed_json != None) :
            for field, string in parsed_json.iteritems() :
                #logging.log(logging.INFO, type(v))
                data = cls.putEntity(field, string)
                if data is None: continue
                data_list.append(data)
        return data_list

def getCanonicalData(key):
    assert isinstance(key, ndb.Key)
    MEMCACHE_KEY = "akafkljacuiudrt2po8vxdzskj" + str(key)
    client = Client()
    canonical_data_key = client.get(MEMCACHE_KEY)
    if canonical_data_key: return canonical_data_key
    data = key.get()
    if data is None: return None
    assert isinstance(data, Data)
    query = data.queryDuplication()
    canonical_data_key = query.get(keys_only=True)
    assert isinstance(canonical_data_key, ndb.Key)
    assert data.dataId >= canonical_data_key.get().dataId
    assert data.field == canonical_data_key.get().field
    assert data.string == canonical_data_key.get().string
    client.set(MEMCACHE_KEY, canonical_data_key)
    return canonical_data_key

def getCanonicalDataList(key_list):
    result = []
    for key in key_list:
        #assert isinstance(key, ndb.Key)
        canonical_data_key = getCanonicalData(key)
        result.append(canonical_data_key)
    return result

def isEquivalentDataKeyList(l1, l2):
    if len(l1) != len(l2): return False
    for i in range(len(l1)):
        k1 = l1[i]
        if not k1: return False 
        else: e1 = k1.get()
        k2 = l2[i]
        if not k2: return False 
        else: e2 = k2.get()
        if e1.field != e2.field: return False
        if e1.string != e2.string: return False
    return True
