from lib.JsonRpc import JsonRpcDispatcher, JsonRpcResponse, JsonRpcRequest
from model.RawDataNdb import RawData
from model.MetadataNdb import Metadata
from google.appengine.ext.key_range import ndb
from google.appengine.api import memcache
from logging import debug
from datetime import datetime, timedelta
#from google.appengine.ext import ndb

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
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])
        query = RawData.queryRange(start, end)
        keys = query.fetch(keys_only=True, limit=100)
        for key in keys:
            raw_data = key.get()
            assert isinstance(raw_data, RawData)
            jresponse.addResult(raw_data)
        
class _Recent(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        try:
            limit = int(jrequest["params"]["limit"])
        except:
            limit = 1000
        jresponse.setId()
        query = RawData.queryRecent()
        
        client = memcache.Client()
        keys = client.get("recent_items", namespace=unicode(_Recent))
        if keys:
            jresponse.setExtraValue("memcache", "hit")
        if not keys:
            jresponse.setExtraValue("memcache", "missed and reloaded")
            keys = query.fetch(keys_only=True, limit=limit)
            client.set("recent_items", keys, namespace=unicode(_Recent), time=20)

        for key in keys:
            raw_data = key.get()
            assert isinstance(raw_data, RawData)
            jresponse.addResult(raw_data)

class _OneDay(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = jrequest.getPathInfo()
        try:
            year = int(path_info[3])
            month = int(path_info[4])
            day = int(path_info[5])
        except:
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
            jresponse.addResult([metadata.receivedDateTime.isoformat(), rawdata.query])

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
        end = start + timedelta(hours=1)
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
            jresponse.addResult([metadata.receivedDateTime.isoformat(), rawdata.query])


if __name__ == "__main__":
    mapping = []
    mapping.append(("/record/RawData/[0-9]+/[0-9]+/[0-9]+/[0-9]+", _OneHour))
    mapping.append(("/record/RawData/[0-9]+/[0-9]+/[0-9]+/", _OneDay))
    mapping.append(('/record/RawData/[0-9]+/[0-9]+', _Range))
    mapping.append(('/record/RawData', _Recent))
    from lib import WSGIApplication
    application = WSGIApplication(mapping)
    from lib import run_wsgi_app
    run_wsgi_app(application)
