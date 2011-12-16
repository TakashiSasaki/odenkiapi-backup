from  google.appengine.ext import db
from  google.appengine.ext.webapp import Request
from urlparse import urlparse
import logging
from Sender import  Sender
from RawData import RawData
from Data import Data
import datetime
from Counter import Counter

class Metadata(db.Model):
    metadataId = db.IntegerProperty()
    receivedDateTime = db.DateTimeProperty()
    sender = db.ReferenceProperty(Sender)
    rawData = db.ReferenceProperty(RawData)
    dataList = db.ListProperty(db.Key)

def GetMetadata(sender_, raw_data, data_list):
    metadata = Metadata()
    metadata.metadataId = Counter.GetNextId("metadataId")
    now = datetime.datetime.now()
    logging.info(now.strftime('%Y/%m/%d %H:%M:%S%z'))
    metadata.receivedDateTime = now 
    metadata.sender = sender_
    metadata.rawData = raw_data
    metadata.dataList = data_list
    return metadata.put()
