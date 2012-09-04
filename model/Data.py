from google.appengine.ext import db
from google.appengine.ext.webapp import Request
#import types,logging
from model.Counter import Counter
#import json
from django.utils import simplejson

class Data(db.Model):
    dataId = db.IntegerProperty()
    field = db.StringProperty()
    string = db.StringProperty()

def putData(k,v):
    existing = Data.gql("WHERE name = :1 AND string = :2", k, v).get()
    if existing is not None:
        return existing
    data = Data()
    data.dataId = Counter.GetNextId("dataId")
    data.field = k
    data.string = v
    return data.put()
    
def putDataList(request):
    assert isinstance(request, Request)
    data_list = []
    for k in request.arguments():
        vlist = request.get_all(k)
        #logging.info((k,vlist))
        assert isinstance(vlist, list)
        for v in vlist:
            data = putData(k,v)
            if data is None: continue
            data_list.append(data)
            
    try:
        parsed_json = simplejson.loads(request.body)
    except ValueError:
        parsed_json = None

    if (parsed_json != None) :
        for k, v in parsed_json.iteritems() :
            #logging.log(logging.INFO, type(v))
            data = putData(k,v)
            if data is None: continue
            data_list.append(data)

    return data_list
