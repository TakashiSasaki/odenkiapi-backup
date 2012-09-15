from __future__ import unicode_literals, print_function
from logging import debug 
from lib.gae import JsonRpcDispatcher, run_wsgi_app
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data
from google.appengine.ext import ndb
from model.MetadataNdb import Metadata
from google.appengine.api.memcache import Client
from datetime import datetime, timedelta

def _getDataListByArduinoId(arduino_id):
    arduino_id = unicode(arduino_id)
    MEMCACHE_KEY = "kjasnbargasenanviajfiafjjoi" + arduino_id
    client = Client()
    data_list = client.get(MEMCACHE_KEY)
    if not isinstance(data_list, list):
        query = Data.queryByFieldAndString("arduinoid", arduino_id)
        data_list = query.fetch(keys_only=True)
        client.set(MEMCACHE_KEY, data_list)
    return data_list

def _DataListToDict(data_list):
    d = {}
    for data in data_list:
        assert isinstance(data, ndb.Key)
        data_entity = data.get()
        assert isinstance(data_entity, Data)
        d[data_entity.field] = data_entity.string
    return d 

class _OneDay(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            arduino_id = unicode(jrequest.getPathInfo(3))
            year = int(jrequest.getPathInfo(4))
            month = int(jrequest.getPathInfo(5))
            day = int(jrequest.getPathInfo(6))
            hour = int(jrequest.getPathInfo(7))
        except Exception, e:
            jresponse.setError(JsonRpcError.INVALID_REQUEST, "Try /record/Arduino/<arduinoid>/<year>/<month>/<day> %s." % e.message())
            return
        
        try:
            data_keys = Data.fetchByFieldAndString("arduinoid", arduino_id)
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        
        start = datetime(year=year, month=month, day=day, hour=hour)
        end = start + timedelta(hours=1) + timedelta(minutes=1)
        start = start - timedelta(minutes=1)
        #data_list = _getDataListByArduinoId(arduino_id)
        #jresponse.setExtraValue("data_list", data_list)

        metadata_keys = Metadata.fetchDateRangeAndDataList(start, end, data_keys)

        for metadata_key in metadata_keys:
            metadata_entity = metadata_key.get()
            assert isinstance(metadata_entity, Metadata)
            data_dict = _DataListToDict(metadata_entity.dataList)
            jresponse.addResult([metadata_entity.receivedDateTime.isoformat(), data_dict.get("time"), data_dict.get("gen.power(W)"), data_dict.get("duration")])
        jresponse.setFieldNames(["receivedDateTime", "time", "gen.power(W)", "duration"])
        
class _Recent(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            arduinoid = unicode(jrequest.getPathInfo(3))
            data_keys = Data.fetchByFieldAndString("arduinoid", arduinoid)
            assert data_keys
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        metadata_keys = Metadata.fetchByDataList(data_keys)
        for metadata_key in metadata_keys:
            metadata_entity = metadata_key.get()
            data_list = metadata_entity.dataList
            data_dict = _DataListToDict(data_list)
            jresponse.addResult([metadata_entity.receivedDateTime.isoformat(), data_dict.get("time"), data_dict.get("gen.power(W)"), data_dict.get("duration")])

if __name__ == "__main__":
    mapping = []
    mapping.append(("/record/Arduino/[^/]+", _Recent))
    mapping.append(("/record/Arduino/[^/]+/[0-9]+/[0-9]+/[0-9]+/[0-9]+", _OneDay))
    run_wsgi_app(mapping)

