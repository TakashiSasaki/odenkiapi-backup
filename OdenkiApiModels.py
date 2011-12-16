from  google.appengine.ext import db
from  google.appengine.ext.webapp import Request
from urlparse import urlparse
import logging

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
    ipAddress = db.StringProperty()
    port = db.IntegerProperty()
    protocol = db.StringProperty()

def GetSender(request):
    assert isinstance(request, Request)
    ip_address = request.remote_addr
    parsed_url = urlparse(request.url)
    if parsed_url.scheme == "http":
        protocol = "http"
        port = 80
    elif parsed_url["scheme"] == "https":
        protocol = "https"
        port = 443
    else:
        protocol = ""
        port = -1
    logging.info((ip_address, port, protocol))
    gql_query = Sender.gql("WHERE ipAddress = :1 AND port = :2 AND protocol = :3", ip_address, port, protocol)
    existing_sender = gql_query.get()
    logging.info(existing_sender)
    if existing_sender is not None:
        logging.info((existing_sender.senderId, existing_sender.ipAddress, existing_sender.port, existing_sender.protocol))
        return existing_sender
    else:
        sender = Sender()
        sender.senderId = Counter.GetNextId("senderId")
        sender.ipAddress = ip_address
        sender.port = port
        sender.protocol = protocol
        return sender.put() 

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
