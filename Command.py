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
from datetime import datetime

class Command(db.Model):
    commandId = db.IntegerProperty()
    equipmentId = db.StringProperty()
    userId = db.StringProperty()
    command = db.StringProperty()
    result = db.StringProperty()
    queuedDateTime = db.DateTimeProperty()
    attemptDateTimes = db.ListProperty(datetime)
    executedDateTime = db.DateTimeProperty()
