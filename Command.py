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
from MyRequestHandler import MyRequestHandler
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app

class Command(db.Model):
    commandId = db.IntegerProperty()
    equipmentId = db.StringProperty()
    userId = db.StringProperty()
    command = db.StringProperty()
    result = db.StringProperty()
    queuedDateTime = db.DateTimeProperty()
    attemptDateTimes = db.ListProperty(datetime)
    executedDateTime = db.DateTimeProperty()

class _RequestHandler(MyRequestHandler):
    def get(self):
        query = Command.all()
        query.order("-queuedDateTime")
        result = query.run()
        vv = []
        for x in result:
            v = {}
            v["commandId"] = x.commandId
            v["equipmentId"] = x.equipmentId
            v["userId"] = x.userId
            v["command"] = x.command
            v["result"] = x.result
            v["queuedDateTime"] = x.queuedDateTime
            v["attemptedDateTimes"] = x.attemptDateTimes.join()
            v["executedDateTime"] = x.executedDateTime
            vv.append(v)
        self.writeWithTemplate({"commands": vv}, "Command")
        
    def post(self):
        pass
        
if __name__ == "__main__":
    application = WSGIApplication([('/Command', _RequestHandler)], debug=True)
    run_wsgi_app(application)
