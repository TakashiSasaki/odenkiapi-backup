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

class Equipment(db.Model):
    senderId = db.IntegerProperty()
    equipmentId = db.IntegerProperty()
    userId = db.IntegerProperty()
    commands = db.StringListProperty()
    results = db.StringListProperty()
    queuedDateTime = db.DateTimeProperty()
    lastResponse = db.DateTimeProperty()
    executedDateTime = db.DateTimeProperty()
