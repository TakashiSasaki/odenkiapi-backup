#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from model.Counter import Counter
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityDuplicated, EntityNotFound, EntityExists
from model.DataNdb import Data
from model.NdbModel import NdbModel

class Sensor(NdbModel):
    uniqueSensorId = ndb.IntegerProperty()
    #senderIds = ndb.IntegerProperty(repeated=True)
    #equipmentName = ndb.StringProperty(indexed=False)
    productName = ndb.IntegerProperty()
    serialNumber = ndb.IntegerProperty()
    moduleId = ndb.IntegerProperty()
    sensorId = ndb.IntegerProperty()
    sensorName = ndb.IntegerProperty(indexed=False)
    odenkiId = ndb.IntegerProperty()
    #field = ndb.StringProperty()
    #string = ndb.StringProperty()

    @classmethod
    def create(cls, product_name_tuple, serial_number_tuple, module_id_tuple, sensor_id_tuple, sensor_name_tuple, odenki_id):
        assert isinstance(odenki_id, int)
        assert isinstance(product_name_tuple, tuple)
        assert isinstance(serial_number_tuple, tuple)
        assert isinstance(module_id_tuple, tuple)
        assert isinstance(sensor_id_tuple, tuple)
        assert isinstance(sensor_name_tuple, tuple)
        
        product_name = Data.prepare(product_name_tuple)
        serial_number = Data.prepare(serial_number_tuple)
        module_id = Data.prepare(module_id_tuple)
        sensor_id = Data.prepare(sensor_id_tuple)
        sensor_name = Data.prepare(sensor_name_tuple)
        try:
            existing_sensor = cls.getByProductAndSerial(product_name, serial_number, module_id, sensor_id)
            raise EntityExists("Equipment", {"product_name":product_name_tuple, "serial_number": serial_number_tuple, "module_id": module_id_tuple, "sensor_id": sensor_id_tuple })
        except: 
            sensor = Sensor()
            sensor.uniqueSensorId = Counter.GetNextId("equipmentId")
            sensor.productName = product_name
            sensor.serialNumber = serial_number
            sensor.moduleId = module_id
            sensor.sensorId = sensor_id
            sensor.odenkiId = odenki_id
            sensor.put()
            return sensor
    
    @classmethod
    def getByProductAndSerial(cls, product_name, serial_number, module_id, sensor_id, sensor_name, odenki_id):
        assert isinstance(product_name, int) and isinstance(serial_number, int) and isinstance(module_id, int)and isinstance(sensor_id, int)and isinstance(sensor_name, int) and isinstance(odenki_id, int)
        query = ndb.Query(kind="Sensor")
        query = query.filter(cls.productName == product_name)
        query = query.filter(cls.serialNumber == serial_number)
        query = query.filter(cls.moduleId == module_id)
        query = query.filter(cls.sensorId == sensor_id)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound("Sensor", {"product_name":product_name, "serial_number":serial_number, "module_id": module_id, "sensor_id":sensor_id})
        if len(keys) == 2:
            raise EntityDuplicated({"product_name":product_name, "serial_number":serial_number, "module_id":module_id, "sensor_id":sensor_id})
        return keys[0].get()

    @classmethod
    def getByUniqueSensorId(cls, unique_sensor_id):
        query = ndb.Query(kind="Sensor")
        query = query.filter(Sensor.uniqueSensorId == unique_sensor_id)
        keys = query.get(keys_only=True, limit=2)
        if len(keys >= 2):
            raise EntityDuplicated({"equipmentId":unique_sensor_id})
        if len(keys == 0):
            raise EntityNotFound({"equipmentId":unique_sensor_id})
        return keys[0].get()
