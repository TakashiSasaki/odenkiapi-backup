from __future__ import unicode_literals, print_function
from lib.JsonRpc import *
from urlparse import urlparse
from model.DataNdb import Data, getCanonicalData
from google.appengine.ext import ndb
from logging import debug

class _Recent(JsonRpcDispatcher):

    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            limit = int(jrequest.getValue("limit"))
        except:
            limit = 100
        jresponse.setExtraValue("limit", limit)
        query = Data.queryRecent()
        keys = query.fetch(keys_only=True, limit=limit)
        for k in keys:
            assert isinstance(k, ndb.Key)
            e = k.get()
            assert isinstance(e, Data)
            jresponse.addResult(e)
        
class _Range(JsonRpcDispatcher):

    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])
        
        query = Data.queryRange(start, end)
        #query = query.filter(Data.dataId >= start)
        #query = query.filter(Data.dataId <= end)
        
        keys = query.fetch(keys_only=True)
        for key in keys:
            entity = key.get()
            assert isinstance(entity, Data)
            jresponse.addResult(entity)
        

    def PUT(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        query_string = urlparse(self.request.url)[4]
        debug(query_string)
        if len(query_string) > 0:
            keys = Data.putParams(query_string)
            self.response.out.write("keys = %s" % keys)
            return
        
class _ByDataId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            data_id = int(jrequest.getPathInfo()[3])
        except: return
        query = Data.querySingle(data_id)
        data_key = query.get(keys_only=True)
        data = data_key.get()
        assert isinstance(data, Data)
        jresponse.addResult(data)
        jresponse.setExtraValue("key_id", data_key.id())

class _DuplicationCheck(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        LIMIT = 100
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            start = int(jrequest.getValue("start")[0])
            end = int(jrequest.getValue("end")[0])
        except:
            jresponse.setError(JsonRpcError.INVALID_PARAMS, "start and end are mandatory")
            return
        query = Data.queryRange(start, end)
        keys = query.fetch(keys_only=True, limit=LIMIT)
        for key in keys:
            data = key.get()
            assert isinstance(data, Data)
            query_for_duplicated_data = data.queryDuplication()
            assert isinstance(query_for_duplicated_data, ndb.Query)
            keys_for_duplicated_data = query_for_duplicated_data.fetch(keys_only=True)
            if len(keys_for_duplicated_data) <= 1: continue
            jresponse.addResult([data.dataId, data.field, data.string, getCanonicalData(key).get().dataId])
        jresponse.setExtraValue("limit", LIMIT)

class _ByKeyId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            key_id = int(jrequest.getPathInfo()[4])
        except: return
        data_key = ndb.Key(Data, key_id)
        jresponse.addResult(data_key.get())
        jresponse.setExtraValue("key_id", key_id)
        
if __name__ == "__main__":
    mapping = []
    mapping.append(("/record/Data", _Recent))
    mapping.append(("/record/Data/[0-9]+", _ByDataId))
    mapping.append(("/record/Data/id/[0-9]+", _ByKeyId))
    mapping.append(("/record/Data/[0-9]+/[0-9]+", _Range))
    mapping.append(("/record/Data/duplicated", _DuplicationCheck))
    from lib import WSGIApplication
    application = WSGIApplication(mapping, debug=True)
    from lib import run_wsgi_app
    run_wsgi_app(application)
