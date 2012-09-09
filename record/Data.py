from __future__ import unicode_literals, print_function
from lib.JsonRpc import JsonRpcDispatcher, JsonRpcRequest, JsonRpcResponse
from urlparse import urlparse
from model.DataNdb import Data
from google.appengine.ext import ndb
from logging import debug

class _RecentData(JsonRpcDispatcher):

    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        debug("%s" % Data)
        query = Data.getByDataIdDescending()
        keys = query.fetch(keys_only=True)
        for k in keys:
            assert isinstance(k, ndb.Key)
            e = k.get()
            assert isinstance(e, Data)
            jresponse.addResult([e.dataId, e.field, e.string])
            #self.response.out.write("%s, %s, %s \n" % (e.dataId, e.field, e.string))
        #self.response.content_type = "text/plain"
        
        
class _Data(JsonRpcDispatcher):

    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])
        
        query = Data.getByDataIdDescending()
        query = query.filter(Data.dataId >= start)
        query = query.filter(Data.dataId <= end)
        
        keys = query.fetch(keys_only=True)
        for key in keys:
            entity = key.get()
            assert isinstance(entity, Data)
            jresponse.addResult([entity.dataId, entity.field, entity.string])
        

    def PUT(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        query_string = urlparse(self.request.url)[4]
        debug(query_string)
        if len(query_string) > 0:
            keys = Data.putParams(query_string)
            self.response.out.write("keys = %s" % keys)
            return
        
if __name__ == "__main__":
    from google.appengine.ext.webapp import WSGIApplication
    mapping = []
    mapping.append(("/record/Data", _RecentData))
    mapping.append(("/record/Data/[0-9]+/[0-9]+", _Data))
    application = WSGIApplication(mapping, debug=True)
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(application)
