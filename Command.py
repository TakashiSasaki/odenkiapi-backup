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
from OdenkiUser import getCurrentUser, OdenkiUser
from simplejson import loads
from Counter import Counter

class Command(db.Model):
    commandId = db.IntegerProperty()
    equipmentId = db.StringProperty()
    userId = db.StringProperty()
    command = db.StringProperty()
    result = db.StringProperty()
    queuedDateTime = db.DateTimeProperty()
    attemptDateTimes = db.ListProperty(datetime)
    executedDateTime = db.DateTimeProperty()
    
class CommandNotFound(Exception):
    pass

def getCommandById(command_id):
    query = Command.all()
    query.filter("commandId = ", command_id)
    result = query.fetch(10)
    if len(result) > 1:
        raise RuntimeError("duplicated command id")
    if len(result) == 0:
        raise CommandNotFound 
    return result[0]

def registerNewCommand(dict):
    pass

def renewCommand(dict):
    command = getCommandById(dict["commandId"])
    assert isinstance(command, Command)
    command.equipmentId = dict["equipmentId"]
    command.userId = dict["userId"]
    command.command = dict["command"]
    command.queuedDateTime = datetime.datetime.now()
    command.put()

def registerCommand(dict):
    command = Command()
    assert isinstance(command, Command)
    command.commandId = Counter.GetNextId("commandId")
    command.equipmentId = dict["equipmentId"]
    command.userId = dict["userId"]
    command.command = dict["command"]
    command.queuedDateTime = datetime.datetime.now()
    command.put()

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
        odenki_user = getCurrentUser()
        assert isinstance(odenki_user, OdenkiUser)
        parsed_json = loads(self.request.body)
        parsed_json["userId"] = odenki_user.odenkiId
        try:
            renewCommand(parsed_json)
        except CommandNotFound:
            registerCommand(parsed_json)
        
if __name__ == "__main__":
    application = WSGIApplication([('/Command', _RequestHandler)], debug=True)
    run_wsgi_app(application)
