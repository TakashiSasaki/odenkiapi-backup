#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from model.Counter import Counter
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityDuplicated, EntityNotFound

class Equipment(ndb.Model):
    equipmentId = ndb.IntegerProperty()
    senderIds = ndb.IntegerProperty(repeated=True)
    equipmentName = ndb.StringProperty(indexed=False)
    odenkiId = ndb.IntegerProperty()
    field = ndb.StringProperty()
    string = ndb.StringProperty()

    @classmethod
    def createNew(cls, odenki_id, field, string):
        equipment = Equipment()
        equipment.equipmentId = Counter.GetNextId("equipmentId")
        equipment.odenkiId = odenki_id
        equipment.put()
    
    @classmethod
    def getByEquipmentId(cls, equipment_id):
        query = ndb.Query(kind="Equipment")
        query = query.filter(Equipment.equipmentId == equipment_id)
        keys = query.get(keys_only=True, limit=2)
        if len(keys >= 2):
            raise EntityDuplicated({"equipmentId":equipment_id})
        if len(keys == 0):
            raise EntityNotFound({"equipmentId":equipment_id})
        return keys[0].get()
