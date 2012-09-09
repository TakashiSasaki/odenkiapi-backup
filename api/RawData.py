'''
Created on 2012/09/04

@author: sasaki
'''
from lib.JsonRpc import JsonRpcDispatcher, JsonRpcRequest, JsonRpcResponse
from google.appengine.ext.ndb import Key
from model.RawDataNdb import RawData

class RecentRawData(JsonRpcDispatcher):
    
    def GET(self, json_rpc_request, jresponse):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        #start = json_rpc_request.getValue("start")
        #end = json_rpc_request.getValue("end")
        limit = json_rpc_request.getValue("limit")
        if not isinstance(limit, int):
            limit = int(limit[0])
        
        json_rpc_response = JsonRpcResponse(json_rpc_request.getId())
        fieldnames = RawData.getFieldNames()
        #lib.debug("fieldnames = %s" % fieldnames)
        json_rpc_response.setFieldNames(fieldnames)
        
        q = RawData.queryRecent()
        for key in q.fetch(keys_only=True, limit=limit):
            entity = key.get()
            if not isinstance(entity, RawData) : continue
            json_dict = entity.to_dict()
            if not isinstance(json_dict, dict) : continue
            json_rpc_response.addResult(json_dict)

        return json_rpc_response

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/RawData", RecentRawData))
    from lib import WSGIApplication
    application = WSGIApplication(mapping, debug=True)
    from lib import run_wsgi_app
    run_wsgi_app(application)
