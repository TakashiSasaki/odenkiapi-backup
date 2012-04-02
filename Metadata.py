from  google.appengine.ext import db
from  google.appengine.ext.webapp import Request
from urlparse import urlparse
import logging
from Sender import  Sender
from RawData import RawData
from Data import Data
import datetime
from Counter import Counter
from google.appengine.api import memcache

class Metadata(db.Model):
    metadataId = db.IntegerProperty()
    receivedDateTime = db.DateTimeProperty()
    sender = db.ReferenceProperty(Sender)
    rawData = db.ReferenceProperty(RawData)
    dataList = db.ListProperty(db.Key)
    executedCommandIds = db.ListProperty(int)
    executedResults = db.StringListProperty()

def putMetadata(sender_, raw_data, data_list):
    metadata = Metadata()
    metadata.metadataId = Counter.GetNextId("metadataId")
    now = datetime.datetime.now()
    logging.info(now.strftime('%Y/%m/%d %H:%M:%S%z'))
    metadata.receivedDateTime = now 
    metadata.sender = sender_
    metadata.rawData = raw_data
    metadata.dataList = data_list
    return metadata.put()

memcache_client = memcache.Client()

def getMetadata(key):
    metadata_entity = memcache_client.get(str(key))
    if metadata_entity is None:
        metadata_entity = db.get(key)
    return metadata_entity

def getDataIds(metadata):
    assert isinstance(metadata, Metadata)
    data_ids = []
    for data_key in metadata.dataList:
        data_ids.append(getDataId(data_key))
    return data_ids

def getDataId(key):
    key_string = str(key)+"dataId"
    data_id = memcache_client.get(key_string)
    if data_id is not None:
        return data_id
    data_entity = db.get(key)
    assert isinstance(data_entity, db.Model)
    assert data_entity.kind() == "Data"
    memcache_client.set(key_string, data_entity.dataId)
    return data_entity.dataId
