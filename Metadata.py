from  google.appengine.ext import db
from  google.appengine.ext.webapp import Request
from urlparse import urlparse
import logging
import Sender, RawData
from Data import Data

class Metadata(db.Model):
    receivedDateTime = db.DateTimeProperty()
    sender = db.ReferenceProperty(Sender)
    rawData = db.ReferenceProperty(RawData)
    data = db.ReferenceProperty(Data)
