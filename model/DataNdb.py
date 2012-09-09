from __future__ import unicode_literals
from logging import debug
from google.appengine.ext import ndb
from google.appengine.ext.webapp import Request
#import types,logging
from model.Counter import Counter
from django.utils import simplejson

class Data(ndb.Model):
    dataId = ndb.IntegerProperty()
    field = ndb.StringProperty()
    string = ndb.StringProperty()
    
    @classmethod
    def getByDataIdDescending(cls):
        query = ndb.Query(kind="Data")
        query = query.order(-Data.dataId)
        return query
    
    @classmethod
    def getByDataId(cls, data_id):
        assert isinstance(data_id, int)
        query = ndb.Query(kind="Data")
        query = query.filter(cls.dataId == data_id)
        return query
    
    @classmethod
    def getByFieldAndString(cls, field, string):
        assert isinstance(field, unicode)
        assert isinstance(string, unicode)
        query = ndb.Query(kind="Data")
        query = query.filter(cls.field == field)
        query = query.filter(cls.string == string)
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
            parsed_json = simplejson.loads(request.body)
        except ValueError:
            parsed_json = None
    
        if (parsed_json != None) :
            for field, string in parsed_json.iteritems() :
                #logging.log(logging.INFO, type(v))
                data = cls.putEntity(field, string)
                if data is None: continue
                data_list.append(data)
        return data_list
