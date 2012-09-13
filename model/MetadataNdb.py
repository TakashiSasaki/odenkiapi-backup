from __future__ import unicode_literals, print_function
from google.appengine.ext import ndb
from model.SenderNdb import  Sender
from model.RawDataNdb import RawData
from model.Counter import Counter
from datetime import datetime
from logging import debug, info
from model.NdbModel import NdbModel
from model.Columns import Columns
from lib.util import isiterable

class MetadataColumns(Columns):

    def __init__(self):
        Columns.addNumber("metadataId")
        Columns.addDateTime("receivedDateTime")
        Columns.addString("sender")
        Columns.addString("rawData")
        Columns.addString("dataList")
        Columns.addString("executedCommandIds")
        Columns.addString("executedResults")

class Metadata(NdbModel, MetadataColumns):
    
    metadataId = ndb.IntegerProperty()
    receivedDateTime = ndb.DateTimeProperty()
    sender = ndb.KeyProperty()
    rawData = ndb.KeyProperty()
    dataList = ndb.KeyProperty(repeated=True)
    executedCommandIds = ndb.IntegerProperty(repeated=True)
    executedResults = ndb.StringProperty(repeated=True)
    
    #fieldnames = ["metadataId", "receivedDateTime", "sender", "rawData", "dataList", "executedCommandIds", "executedResults" ]
    
#    def getFields(self):
#        fields = []
#        fields.append(self.metadataId)
#        fields.append(self.receivedDateTime)
#        fields.append(self.sender)
#        fields.append(self.rawData)
#        fields.append(self.dataList)
#        #fields.append(self.executedCommandIds)
#        #fields.append(self.executedResults)
#        return fields
        
    @classmethod
    def queryRecent(cls):
        query = ndb.Query(kind="Metadata")
        query = query.order(-cls.metadataId)
        return query
    
    @classmethod
    def queryRange(cls, start, end):
        assert isinstance(start, int)
        assert isinstance(end, int)
        query = ndb.Query(kind="Metadata")
        query = query.order(-cls.metadataId)
        if start <= end:
            query = query.filter(cls.metadataId >= start)
            query = query.filter(cls.metadataId <= end)
            return query
        else:
            query = query.filter(cls.metadataId <= start)
            query = query.filter(cls.metadataId >= end)
            return query
    
    @classmethod
    def fetchRange(cls, start, end, limit=100):
        return cls.queryRange(start, end).fetch(keys_only=True, limit=limit)
        
    @classmethod
    def queryDateRange(cls, start, end):
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        query = ndb.Query(kind="Metadata")
        if start <= end:
            query = query.filter(cls.receivedDateTime >= start)
            query = query.filter(cls.receivedDateTime <= end)
            return query
        else:
            query = query.filter(cls.receivedDateTime <= start)
            query = query.filter(cls.receivedDateTime >= end)
            query = query.order(-cls.receivedDateTime)
            return query

    @classmethod
    def queryDateRangeAndData(cls, start, end, data):
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        query = ndb.Query(kind="Metadata")
        if start <= end:
            query = query.filter(cls.receivedDateTime >= start)
            query = query.filter(cls.receivedDateTime <= end)
            query = query.filter(cls.dataList == data)
            return query
        else:
            query = query.filter(cls.receivedDateTime <= start)
            query = query.filter(cls.receivedDateTime >= end)
            query = query.order(-cls.receivedDateTime)
            query = query.filter(cls.dataList == data)
            return query
        
    @classmethod
    def queryAfter(cls, start):
        assert isinstance(start, datetime)
        query = ndb.Query(kind="Metadata")
        return query
        
    @classmethod
    def queryByData(cls, data_key):
        assert isinstance(data_key, ndb.Key)
        query = ndb.Query(kind="Metadata")
        query = query.filter(cls.dataList == data_key)
        return query
    
    @classmethod
    def fetchByData(cls, data_key):
        return cls.queryByData(data_key).fetch(keys_only=True, limit=100)
    
    @classmethod
    def putMetadata(cls, sender, raw_data, data_keys):
        assert isinstance(sender, Sender)
        assert isinstance(raw_data, RawData)
        assert isinstance(data_keys, list)
        metadata = Metadata()
        metadata.metadataId = Counter.GetNextId("metadataId")
        now = datetime.datetime.now()
        info(now.strftime('%Y/%m/%d %H:%M:%S%z'))
        metadata.receivedDateTime = now 
        metadata.sender = sender
        metadata.rawData = raw_data
        metadata.dataList = data_keys
        return metadata.put()
    
    @classmethod
    def fetchDateRangeAndData(cls, start, end, data_key):
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert isinstance(data_key, ndb.Key)
        query = ndb.Query(kind="Metadata")
        query = query.filter(cls.receivedDateTime >= start)
        query = query.filter(cls.receivedDateTime <= end)
        query = query.order(cls.receivedDateTime)
        return query.fetch(keys_only=True)

    @classmethod
    def fetchDateRangeAndDataList(cls, start, end, data_keys):
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert isinstance(data_keys, list)
        
        metadata_keys_set = set()
        for data_key in data_keys:
            metadata_keys_set.update(cls.fetchDateRangeAndData(start, end, data_key))
        return metadata_keys_set
    
    @classmethod
    def fetchByDataList(cls, data_keys):
        assert isiterable(data_keys)
        metadata_keys = set()
        for data_key in data_keys:
            metadata_keys.update(cls.fetchByData(data_key))
        return list(metadata_keys)

def getMetadataByDataList(data_list):
    metadata_set = set()
    for data in data_list:
        query = Metadata.queryByData(data)
        keys = query.fetch(keys_only=True)
        metadata_set.update(keys)
    return metadata_set

def _isIdenticalKeyList(l1, l2):
    if len(l1) != len(l2): return False
    try:
        for x in range(len(l1)):
            if l1[x] != l2[x]: return False
    except: return False
    return True

def _canonicalizeDataOne(key):
    """Canonicalize data in Metadata entity.
    It returns Metadata key when canonicalization succeeded.
    You have to put it by yourself because the entity is left not put. 
    It returns None if no canonicalization is needed or cannot canonicalize because of unexpected situation.
    """
    from model.DataNdb import getCanonicalDataList, isEquivalentDataKeyList
    assert isinstance(key, ndb.Key)
    metadata = key.get()
    assert isinstance(metadata, Metadata)
    if not isinstance(metadata.dataList, list): return
    canonicalized_list = getCanonicalDataList(metadata.dataList)
    if _isIdenticalKeyList(canonicalized_list, metadata.dataList): return
    assert len(canonicalized_list) == len(metadata.dataList)
    if not isEquivalentDataKeyList(canonicalized_list, metadata.dataList): return
    metadata.dataList = canonicalized_list
    return metadata 


from google.appengine.ext.deferred import defer
from google.appengine.runtime import DeadlineExceededError
class Canonicalizer(object):
    
    def __init__(self, start, end):
        self.nextMetadataId = start
        self.end = end
        
    def run(self):
        try:
            self.canonicalizeData()
        except DeadlineExceededError:
            info("remaining metadataId between %s and %s" % (self.nextMetadataId, self.end))
            defer(self.run)
        
    @ndb.toplevel
    def canonicalizeData(self):
        query = Metadata.queryRange(self.nextMetadataId, self.end)
        for metadata_key in query.iter(keys_only=True):
            canonicalized_metadata = _canonicalizeDataOne(metadata_key)
            if not canonicalized_metadata:
                self.nextMetadataId = metadata_key.get().metadataId
                continue
            assert isinstance(canonicalized_metadata, Metadata)
            assert metadata_key == canonicalized_metadata.key
            canonicalized_metadata.put_async()
            self.nextMetadataId = metadata_key.get().metadataId
