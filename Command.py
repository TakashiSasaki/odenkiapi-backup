from  google.appengine.ext import db
from urlparse import urlparse
from logging import debug, getLogger, DEBUG
from Sender import  Sender
from RawData import RawData
from Data import Data
from Counter import Counter
from google.appengine.api import memcache
from datetime import datetime
from MyRequestHandler import MyRequestHandler
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from OdenkiUser import getCurrentUser, OdenkiUser
from simplejson import loads
from Counter import Counter
from webob import MIMEAccept

class Command(db.Model):
    commandId = db.IntegerProperty()
    gatewayId = db.StringProperty()
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
    command.gatewayId = dict["gatewayId"]
    command.equipmentId = dict["equipmentId"]
    command.userId = dict["userId"]
    command.command = dict["command"]
    command.queuedDateTime = datetime.datetime.today()
    command.put()

def registerCommand(dict):
    command = Command()
    assert isinstance(command, Command)
    command.commandId = Counter.GetNextId("commandId")
    command.gatewayId = dict["gatewayId"]
    command.equipmentId = dict["equipmentId"]
    command.userId = str(dict["userId"])
    command.command = dict["command"]
    command.queuedDateTime = datetime.today()
    command.put()
    
class _RequestHandler(MyRequestHandler):
    def get(self):
        debug(self.request.accept)
        assert isinstance(self.request.accept, MIMEAccept)
        odenki_user = getCurrentUser()
        assert isinstance(odenki_user, OdenkiUser)
        query = Command.all()
        query.order("-queuedDateTime")
        result = query.run()
        self.resource = {}
        self.resource["commands"] = []
        for x in result:
            v = {}
            v["commandId"] = x.commandId
            v["gatewayId"] = x.gatewayId
            v["equipmentId"] = x.equipmentId
            v["userId"] = x.userId
            v["command"] = x.command
            v["result"] = x.result
            v["queuedDateTime"] = str(x.queuedDateTime)
            v["attemptedDateTimes"] = str(x.attemptDateTimes[-1]) if x.attemptDateTimes is not None and len(x.attemptDateTimes) > 0 else None
            v["executedDateTime"] = str(x.executedDateTime)
            self.resource["commands"].append(v)
        self.resource["odenkiId"] = odenki_user.odenkiId

        if self.request.accept.accept_html():
            self.resource["commands"] = self.resource["commands"][:10];
            self.writeWithTemplate(self.resource, "Command")
        else:
            self.writeJson(self.resource)
            
    def post(self):
        odenki_user = getCurrentUser()
        assert isinstance(odenki_user, OdenkiUser)
        parsed_json = loads(self.request.body)
        parsed_json["userId"] = odenki_user.odenkiId
        try:
            renewCommand(parsed_json)
        except (CommandNotFound, KeyError):
            registerCommand(parsed_json)
        self.get()
        
    def delete(self):
        pass
        
if __name__ == "__main__":
    getLogger().setLevel(DEBUG)
    application = WSGIApplication([('/Command', _RequestHandler)], debug=True)
    run_wsgi_app(application)
