from  google.appengine.ext import db
from  google.appengine.ext.webapp import Request, RequestHandler, WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from urlparse import urlparse
import logging
from Sender import  Sender
from RawData import RawData
from Data import Data
import datetime
from Counter import Counter
from google.appengine.api import memcache
from google.appengine.ext.webapp import  template


class Equipment(db.Model):
    equipmentId = db.IntegerProperty()
    senderIds = db.ListProperty(int)
    equipmentName = db.StringProperty()
    
    @classmethod
    def getByEquipmentId(cls, equipment_id):
        query = Equipment.all()
        query.filter("equipmentId = ", equipment_id)
        result = query.run()
        equipment  = result.next()
        return equipment
    
    def putByEquipmentId(self):
        equipment = Equipment.getByEquipmentId(self.equipmentId)
        if equipment is None:
            self.put()
        else:
            equipment.senderIds = self.senderIds
            equipment.equipmentName = self.equipmentName

class _RequestHandler(RequestHandler):
    def get(self):
        xx = []
        for x in Equipment.all():
            x = {"equipmentId": x.equipmentId,
                 "equipmentName": x.equipmentName,
                 "senderIds": x.senderIds}
            xx.append(x)
        self.response.out.write(template.render("html/Equipment.html", {"xx":xx}))
        
if __name__ == "__main__":
    x = Equipment()
    x.equipmentId = 100
    x.senderIds = [100]
    x.equipmentName = "test equipment"
    x.putByEquipmentId()
    logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/Equipment', _RequestHandler)], debug=True)
    run_wsgi_app(application)
