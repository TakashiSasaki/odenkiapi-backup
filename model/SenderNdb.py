from __future__ import unicode_literals, print_function
from google.appengine.ext import ndb
from google.appengine.ext.webapp import Request
from urlparse import urlparse
from model.Counter import Counter
from model.NdbModel import NdbModel

class Sender(NdbModel):       
    senderId = ndb.IntegerProperty()
    ipAddress = ndb.StringProperty()
    port = ndb.IntegerProperty()
    protocol = ndb.StringProperty()
    
    fieldnames = ["senderId", "ipAddress", "port", "protocol"]
    
    @classmethod
    def querySender(cls, ip_address, port, protocol):
        assert isinstance(ip_address, unicode)
        assert isinstance(port, int)
        assert isinstance(protocol, unicode)
        query = ndb.Query(kind="Sender")
        query = query.filter(cls.ipAddress == ip_address)
        query = query.filter(cls.port == port)
        query = query.filter(cls.protocol == protocol)
        return query
    
    @classmethod
    def queryRecent(cls):
        query = ndb.Query(kind="Sender")
        query = query.order(-cls.senderId)
        return query
    
    @classmethod
    def fetchRecent(cls, limit=100):
        return cls.queryRecent().fetch(keys_only=True, limit=limit)
    
    @classmethod
    def queryRange(cls, start, end):
        assert isinstance(start, int)
        assert isinstance(end, int)
        query = cls.queryRecent()
        if start <= end:
            query = query.filter(cls.senderId >= start)
            query = query.filter(cls.senderId <= end)
            return query
        else:
            query = query.filter(cls.senderId <= start)
            query = query.filter(cls.senderId >= end)
            return query

    @classmethod
    def fetchRange(cls, start, end):
        return cls.queryRange(start, end).fetch(keys_only=True)

    @classmethod
    def createSender(request):
        #logging.info(("GetSender", request.url))
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
        
        query = Sender.querySender(ip_address, port, protocol)
        existing_sender = query.get(keys_only=True)
        if existing_sender: return existing_sender

        sender = Sender()
        sender.senderId = Counter.GetNextId("senderId")
        sender.ipAddress = ip_address
        sender.port = port
        sender.protocol = protocol
        return sender.put() 
