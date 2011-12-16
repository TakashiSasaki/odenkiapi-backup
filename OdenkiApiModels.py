'''
Created on 2011/11/28

@author: sasaki
'''
from  google.appengine.ext import db

class Counter(db.Model):
    count = db.IntegerProperty()
    
    @classmethod
    def GetNextId(cls, name):
        def txn():
            obj = cls.get_by_key_name(name)
            if obj is None:
                obj = cls(key_name=name, count=0)
            obj.count += 1
            obj.put()
            return obj.count
        return db.run_in_transaction(txn)
    
class Sender(db.Model):
    senderId = db.IntegerProperty()
    ipaddress = db.StringProperty()
    port = db.StringProperty()
    protocol = db.StringProperty()

class RawData(db.Model):
    path = db.StringProperty()
    query = db.StringProperty()
    fragment = db.StringProperty()
    body = db.StringProperty 
    
class Data(db.Model):
    dataId = db.IntegerProperty()
    name = db.StringProperty
    strings = db.StringListProperty()
    number = db.ListProperty(float)

class Metadata(db.Model):
    receivedDateTime = db.DateTimeProperty()
    sender = db.ReferenceProperty(Sender)
    rawData = db.ReferenceProperty(RawData)
    data = db.ReferenceProperty(Data)
