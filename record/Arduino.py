from __future__ import unicode_literals, print_function
from logging import debug 
from lib.JsonRpc import *
from model.DataNdb import Data
from model.MetadataNdb import Metadata
from google.appengine.api.memcache import Client
from datetime import datetime,timedelta

def _getDataListByArduinoId(arduino_id):
    arduino_id = unicode(arduino_id)
    MEMCACHE_KEY = "kjasnbargasenanviajfiafjjoi"+arduino_id
    client = Client()
    data_list = client.get(MEMCACHE_KEY)
    if not isinstance(data_list, list):
        query = Data.queryByFieldAndString("arduinoid", arduino_id)
        data_list = query.fetch(keys_only=True)
        client.set(MEMCACHE_KEY, data_list)
    return data_list



class _OneDay(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = jrequest.getPathInfo()
        try:
            arduino_id = path_info[3]
            year = int(path_info[4])
            month = int(path_info[5])
            day = int(path_info[6])
        except:
            jresponse.setError(JsonRpcError.INVALID_REQUEST, "Try /record/Arduino/<arduinoid>/<year>/<month>/<day> .")
            return
        assert isinstance(arduino_id, str)
        assert isinstance(year, int)
        assert isinstance(month, int)
        assert isinstance(day, int)
        
        start = datetime(year=year, month=month, day=day)
        end = start + timedelta(days=1)
        data_list = _getDataListByArduinoId(arduino_id)
        jresponse.setExtraValue("data_list", data_list)
        metadata_set = set()
        for data in data_list:
            query= Metadata.queryDateRangeAndData(start, end, data)
            keys = query.fetch(keys_only=True)
            metadata_set.update(keys)
        #metadata_set = getMetadataByDataList(data_list)
        jresponse.setExtraValue("metadata_set", list(metadata_set))
        

if __name__ == "__main__":
    mapping=[]
    mapping.append(("/record/Arduino/[^/]+/[0-9]+/[0-9]+/[0-9]+", _OneDay))
    from lib import WSGIApplication
    application = WSGIApplication(mapping)
    from lib import run_wsgi_app
    run_wsgi_app(application)

        
        
