#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from model.Counter import Counter
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityDuplicated, EntityNotFound, EntityExists
from model.DataNdb import Data
from model.NdbModel import NdbModel

class Equipment(NdbModel):
    equipmentId = ndb.IntegerProperty()
    senderIds = ndb.IntegerProperty(repeated=True)
    equipmentName = ndb.StringProperty(indexed=False)
    product = ndb.IntegerProperty()
    serial = ndb.IntegerProperty()
    odenkiId = ndb.IntegerProperty()
    #field = ndb.StringProperty()
    #string = ndb.StringProperty()

    @classmethod
    def create(cls, odenki_id, product_field, product_string, serial_field, serial_string):
        assert isinstance(odenki_id, int)
        assert isinstance(product_field, unicode)
        assert isinstance(product_string, unicode)
        assert  isinstance(serial_field, unicode)
        assert isinstance(serial_string, unicode)
        try:
            product_data = Data.getByFieldAndString(product_field, product_string)
        except EntityNotFound:
            product_data = Data.create(product_field, product_string)
        product = product_data.dataId
        try:
            serial_data = Data.getByFieldAndString(serial_field, serial_string)
        except EntityNotFound:
            serial_data = Data.create(serial_field, serial_string)
        serial = serial_data.dataId
        try:
            existing_equipment = cls.getByProductAndSerial(product, serial)
            raise EntityExists("Equipment", {"product_field":product_field, "product_string": product_string, "product": product, "serial_field": serial_field, "serial_string":serial_string, "serial":serial })
        except: 
            equipment = Equipment()
            equipment.equipmentId = Counter.GetNextId("equipmentId")
            equipment.odenkiId = odenki_id
            equipment.product = product
            equipment.serial = serial
            equipment.put()
            return equipment
    
    @classmethod
    def getByProductAndSerial(cls, product, serial):
        assert isinstance(product, int) and isinstance(serial, int)
        query = ndb.Query(kind="Equipment")
        query = query.filter(cls.product == product)
        query = query.filter(cls.serial == serial)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound("Equipment", {"product":product, "serial":serial})
        if len(keys) == 2:
            raise EntityDuplicated({"product":product, "serial":serial})
        return keys[0].get()

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
