#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from model.Counter import Counter
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityDuplicated, EntityNotFound, EntityExists
from model.DataNdb import Data
#from model.NdbModel import NdbModel
from model.OdenkiUser import OdenkiUser
from model.CsvMixin import CsvMixin
from lib.DataTableMixin import DataTableMixin
from model.Columns import Columns

class SensorColumns(Columns):
    def __init__(self):
        self.addNumber("uniqueSensorId")
        self.addDataString("productName")
        self.addDataString("serialNumber")
        self.addDataString("moduleId")
        self.addDataString("sensorId")
        self.addDataString("sensorName")
        self.addNumber("odenkiId")

class Sensor(ndb.Model, CsvMixin, DataTableMixin):
    uniqueSensorId = ndb.IntegerProperty()
    #senderIds = ndb.IntegerProperty(repeated=True)
    #equipmentName = ndb.StringProperty(indexed=False)
    productName = ndb.IntegerProperty(required=True)
    serialNumber = ndb.IntegerProperty(required=True)
    moduleId = ndb.IntegerProperty(required=True)
    sensorId = ndb.IntegerProperty(required=True)
    sensorName = ndb.IntegerProperty(indexed=False)
    odenkiId = ndb.IntegerProperty(required=True)
    #field = ndb.StringProperty()
    #string = ndb.StringProperty()

    @classmethod
    def create(cls, product_name_data, serial_number_data, module_id_data, sensor_id_data, sensor_name_data, odenki_user):
        assert isinstance(odenki_user, OdenkiUser)
        assert isinstance(product_name_data, Data)
        assert isinstance(serial_number_data, Data)
        assert isinstance(module_id_data, Data)
        assert isinstance(sensor_id_data, Data)
        assert isinstance(sensor_name_data, Data)
        
        try:
            existing_sensor = cls.getByProductNameSerialNumberModuleIdSensorId(product_name_data, serial_number_data, module_id_data, sensor_id_data)
            raise EntityExists("Equipment", {"product_name_data":product_name_data, "serial_number_data": serial_number_data, "module_id_data": module_id_data, "sensor_id_data": sensor_id_data })
        except: 
            sensor = Sensor()
            sensor.uniqueSensorId = Counter.GetNextId("equipmentId")
            sensor.productName = product_name_data.dataId
            sensor.serialNumber = serial_number_data.dataId
            sensor.moduleId = module_id_data.dataId
            sensor.sensorId = sensor_id_data.dataId
            sensor.odenkiId = odenki_user.odenkiId
            assert sensor_name_data.dataId is not None
            sensor.sensorName = sensor_name_data.dataId
            assert sensor.sensorName is not None
            sensor.put()
            return sensor
    
    @classmethod
    def getByProductNameSerialNumberModuleIdSensorId(cls, product_name_data, serial_number_data, module_id_data, sensor_id_data):
        assert isinstance(product_name_data, Data) and isinstance(serial_number_data, Data) and isinstance(module_id_data, Data)and isinstance(sensor_id_data, Data)
        query = ndb.Query(kind="Sensor")
        query = query.filter(cls.productName == product_name_data.dataId)
        query = query.filter(cls.serialNumber == serial_number_data.dataId)
        query = query.filter(cls.moduleId == module_id_data.dataId)
        query = query.filter(cls.sensorId == sensor_id_data.dataId)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound("Sensor", {"product_name_data":product_name_data, "serial_number_data":serial_number_data, "module_id_data": module_id_data, "sensor_id_name":sensor_id_data})
        if len(keys) == 2:
            raise EntityDuplicated({"product_name_data":product_name_data, "serial_number_data":serial_number_data, "module_id_name":module_id_data, "sensor_id_data":sensor_id_data})
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
