from lib.JsonRpc import JsonRpcDispatcher, JsonRpcResponse, JsonRpcRequest, \
    JsonRpcError
from model.MetadataNdb import Metadata as MetadataNdb
from model.Metadata import Metadata as MetadataDb
from model.DataNdb import getCanonicalDataList
from model.DataNdb import Data as DataNdb
from model.Data import Data as DataDb
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from logging import debug

class _Recent(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        LIMIT = 100
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        query = MetadataNdb.queryRecent()
        keys = query.fetch(keys_only=True, limit=LIMIT)
        for key in keys:
            metadata = key.get()
            assert isinstance(metadata, MetadataNdb)
            jresponse.addResult(metadata.to_list())
        jresponse.setExtraValue("limit", LIMIT)
    
class _Range(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        pass
    

def _listifyDataList(data_list):
    result = []
    for data in data_list:
        data_entity = data.get()
        listified_data = data_entity.to_list()
        result.append(listified_data)
    return result

class _MakeTestData(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        
        def create_data(data_id, field, string):
            data = DataDb()
            data.dataId = data_id
            data.field = field
            data.string = string
            return data.put()
        
        def delete_data(start, end):
            query = DataNdb.queryRange(start, end)
            keys = query.fetch(keys_only=True)
            for key in keys: key.delete()
        
        def create_metadata(metadata_id, data_list):
            metadata = MetadataDb()
            metadata.metadataId = metadata_id
            metadata.dataList = data_list
            return metadata.put()
        
        def delete_metadata(start, end):
            query = MetadataNdb.queryRange(start, end)
            keys = query.fetch(keys_only=True)
            for key in keys: key.delete()
        
        def prepare():
            delete_data(1, 4)
            data1_key = create_data(1, "aa", "bb")
            data2_key = create_data(2, "aa", "bb")
            data3_key = create_data(3, "cc", "dd")
            data4_key = create_data(4, "cc", "dd")
            delete_metadata(1, 6)
            create_metadata(1, [data2_key, data4_key])
            create_metadata(2, [data2_key, data4_key])
            create_metadata(3, [data1_key, data3_key])
            create_metadata(4, [data2_key, data2_key])
            create_metadata(5, [data2_key, data3_key])
            create_metadata(6, [data4_key, data4_key])
        
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        prepare()
        query = MetadataNdb.queryRange(1, 6)
        keys = query.fetch(keys_only=True)
        for key in keys:
            debug(key)
            assert isinstance(key, ndb.Key)
            metadata = key.get()
            jresponse.addResult([metadata.metadataId, _listifyDataList(metadata.dataList)])
        

class _CanonicalizeData(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        EXECUTE_TOKEN = "jikkousuru"
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            start = int(jrequest.getValue("start")[0])
            end = int(jrequest.getValue("end")[0])
            execute = jrequest.getValue("execute")[0]
        except Exception, e:
            jresponse.setError(JsonRpcError.INVALID_PARAMS, unicode(e.__class__) + unicode(e))
            return
        query = MetadataNdb.queryRange(start, end)
        keys = query.fetch(keys_only=True)
        #assert len(keys) == abs(start - end) + 1
        count = 0
        for key in keys:
            metadata = key.get()
            assert isinstance(metadata, MetadataNdb)
            if not isinstance(metadata.dataList, list): continue
            canonicalized_list = getCanonicalDataList(metadata.dataList)
            assert len(canonicalized_list) == len(metadata.dataList)
            for i in range(len(canonicalized_list)):
                debug("%s ==> %s" % (metadata.dataList, canonicalized_list))
                assert canonicalized_list[i].get().field == metadata.dataList[i].get().field
                assert canonicalized_list[i].get().string == metadata.dataList[i].get().string
                assert canonicalized_list[i].get().dataId <= metadata.dataList[i].get().dataId
            if execute == EXECUTE_TOKEN:
                metadata.dataList = canonicalized_list
                metadata.put()
                count += 1
            jresponse.addResult([metadata.metadataId, _listifyDataList(metadata.dataList), _listifyDataList(canonicalized_list)])
        jresponse.setExtraValue("count", count)
            
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
            year = 2012
            month = 8
            day = 20
        start = datetime(year=year, month=month, day=day)
        end = start + timedelta(days=1)
        query = MetadataNdb.queryDateRange(start, end)
        keys = query.fetch(limit=24 * 60 + 100, keys_only=True)
        for key in keys:
            jresponse.addResult(key.get().to_list())
            
class _ByMetadataId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = jrequest.getPathInfo()
        try:
            metadata_id = int(path_info[3])
        except: return 
        query = MetadataNdb.queryRange(metadata_id, metadata_id)
        for metadata_key in query.fetch(keys_only=True):
            jresponse.addResult(metadata_key.get())
            jresponse.setExtraValue("key_id", metadata_key.id())

class _ByKeyId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = jrequest.getPathInfo()
        try:
            key_id = int(path_info[4])
        except: return
        key = ndb.Key(MetadataNdb, key_id)
        jresponse.setExtraValue("key_id", key_id)
        jresponse.addResult(key.get())

if __name__ == "__main__":
    mapping = []
    mapping.append(("/record/Metadata", _Recent))
    mapping.append(("/record/Metadata/id/[0-9]+", _ByKeyId))
    mapping.append(("/record/Metadata/[0-9]+", _ByMetadataId))
    mapping.append(("/record/Metadata/[0-9]+/[0-9]+", _Range))
    mapping.append(("/record/Metadata/[0-9]+/[0-9]+/[0-9]+", _OneDay))
    mapping.append(("/record/Metadata/CanonicalizeData", _CanonicalizeData))
    mapping.append(("/record/Metadata/MakeTestData", _MakeTestData))
    from lib import WSGIApplication
    application = WSGIApplication(mapping, debug=True)
    from lib import run_wsgi_app
    run_wsgi_app(application)
