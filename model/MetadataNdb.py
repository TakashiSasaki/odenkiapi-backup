from  google.appengine.ext import ndb
from model.SenderNdb import  Sender
from model.RawDataNdb import RawData
from model.Counter import Counter
import datetime
from logging import debug, info
from model.NdbModel import NdbModel

class Metadata(NdbModel):
    metadataId = ndb.IntegerProperty()
    receivedDateTime = ndb.DateTimeProperty()
    sender = ndb.KeyProperty()
    rawData = ndb.KeyProperty()
    dataList = ndb.KeyProperty(repeated=True)
    executedCommandIds = ndb.IntegerProperty(repeated=True)
    executedResults = ndb.StringProperty(repeated=True)

    @classmethod
    def getFieldNames(cls):
        return ["metadataId", "receivedDateTime", "sender", "rawData", "dataList", "executedCommandids", "executedResults" ]
    
    def getFields(self):
        fields = []
        fields.append(self.metadataId)
        fields.append(self.receivedDateTime)
        fields.append(self.sender)
        fields.append(self.rawData)
        fields.append(self.dataList)
        #fields.append(self.executedCommandIds)
        #fields.append(self.executedResults)
        return fields
        
    @classmethod
    def queryRecent(cls):
        query = ndb.Query(kind="Metadata")
        query = query.order(-cls.metadataId)
        return query
    
    @classmethod
    def queryRange(cls, start, end):
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
