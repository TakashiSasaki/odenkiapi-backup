'''
Created on 2012/09/04

@author: sasaki
'''
from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
from model.RawDataNdb import RawData, RawDataColumns

class RecentRawData(JsonRpcDispatcher):
    
    def GET(self, json_rpc_request, jresponse):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        #start = json_rpc_request.getValue("start")
        #end = json_rpc_request.getValue("end")
        try:
            limit = int(json_rpc_request.getValue("limit")[0])
        except:
            limit = 100
        
        #json_rpc_response = JsonRpcResponse(json_rpc_request.getId())
        #jresponse.setFieldNames(RawDataColumns().getColumnIds())
        jresponse.setColumns(RawDataColumns())
        
        q = RawData.queryRecent()
        for key in q.fetch(keys_only=True, limit=limit):
            entity = key.get()
            if not isinstance(entity, RawData) : continue
            json_dict = entity.to_dict()
            if not isinstance(json_dict, dict) : continue
            jresponse.addResult(json_dict)

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/RawData", RecentRawData))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
