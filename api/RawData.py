# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
from model.RawDataNdb import RawData, RawDataColumns
from google.appengine.api import memcache
from logging import debug
from datetime import datetime, timedelta
from model.MetadataNdb import Metadata

class _Recent(JsonRpcDispatcher):
    MEMCACHE_KEY = "2nanjjkzvxnzfdyiwjbdkj8yiqlkj78ghdkhzd"
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        
        client = memcache.Client()
        keys = client.get(self.MEMCACHE_KEY)
        if keys:
            jresponse.setExtraValue("memcache", "hit")
        else:
            jresponse.setExtraValue("memcache", "missed and reloaded")
            keys = RawData.fetchRecent()
            client.set(self.MEMCACHE_KEY, keys, time=20)

        for key in keys:
            raw_data = key.get()
            assert isinstance(raw_data, RawData)
            jresponse.addResult(raw_data)
        jresponse.setColumns(RawDataColumns())
        
        jresponse.setExtraValue("__name__", __name__)
        jresponse.setExtraValue("__package__", __package__)
        jresponse.setExtraValue("__file__", __file__)
        
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

class _Range(JsonRpcDispatcher):
#    @ndb.toplevel
#    def get(self):
#        path_info = self.request.path_info.split("/")
#        start = int(path_info[3])
#        end = int(path_info[4])
#        q = RawData.queryPeriod(start, end)
#        
#        for raw_data_key in q.fetch(keys_only=True):
#            self.response.out.write(str(raw_data_key.get()))
            
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            start = int(jrequest.getPathInfo(3))
            end = int(jrequest.getPathInfo(4))
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        
        for key in RawData.fetchRange(start, end):
            raw_data = key.get()
            assert isinstance(raw_data, RawData)
            jresponse.addResult(raw_data)
        jresponse.setColumns(RawDataColumns())

class _OneDay(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            year = int(jrequest.getPathInfo(3))
            month = int(jrequest.getPathInfo(4))
            day = int(jrequest.getPathInfo(5))
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        start = datetime(year=year, month=month, day=day)
        end = start + timedelta(days=1)
        start = start - timedelta(minutes=1)
        end = end + timedelta(minutes=1)
        
        metadata_query = Metadata.queryDateRange(start, end)
        metadata_keys = metadata_query.fetch(keys_only=True)
        for metadata_key in metadata_keys:
            metadata = metadata_key.get()
            assert isinstance(metadata, Metadata)
            rawdata_key = metadata.rawData
            rawdata = rawdata_key.get()
            assert isinstance(rawdata, RawData)
            #jresponse.addResult([metadata.receivedDateTime.isoformat(), rawdata.query])
            jresponse.addResult(rawdata)
        jresponse.setColumns(RawDataColumns())

class _OneHour(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = jrequest.getPathInfo()
        try:
            year = int(path_info[3])
            month = int(path_info[4])
            day = int(path_info[5])
            hour = int(path_info[6])
        except:
            return
        start = datetime(year=year, month=month, day=day, hour=hour)
        assert start.tzinfo is None # start is a naive datetime object
        end = start + timedelta(hours=1)
        assert end.tzinfo is None # end is a naive datetime object
        start = start - timedelta(minutes=1)
        end = end + timedelta(minutes=1)
        
        metadata_query = Metadata.queryDateRange(start, end)
        metadata_keys = metadata_query.fetch(keys_only=True)
        for metadata_key in metadata_keys:
            metadata = metadata_key.get()
            assert isinstance(metadata, Metadata)
            rawdata_key = metadata.rawData
            rawdata = rawdata_key.get()
            assert isinstance(rawdata, RawData)
            #jresponse.addResult([metadata.receivedDateTime.isoformat(), rawdata.query])
            jresponse.addResult(rawdata)
        jresponse.setColumns(RawDataColumns())

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/RawData/[0-9]+/[0-9]+/[0-9]+/[0-9]+", _OneHour))
    mapping.append(("/api/RawData/[0-9]+/[0-9]+/[0-9]+", _OneDay))
    mapping.append(('/api/RawData/[0-9]+/[0-9]+', _Range))
    mapping.append(("/api/RawData", _Recent))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)
