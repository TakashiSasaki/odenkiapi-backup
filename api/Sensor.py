#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from google.appengine.ext import ndb
from model.Sensor import Sensor
from google.appengine.ext.webapp import Request
from lib.gae import run_wsgi_app
from lib.json.JsonRpcError import InvalidParams, EntityExists, EntityNotFound
from model.DataNdb import Data
from gaesessions import get_current_session
from model.OdenkiUser import OdenkiUser
from test.test_pprint import uni

class Enumerate(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        query = ndb.Query(kind="Sensor")
        query = query.order(-Sensor.uniqueSensorId)
        keys = query.fetch(keys_only=True, limit=100)
        for key in keys:
            jresponse.addResult(key.get())
            
    def register(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        request = jrequest.request
        assert isinstance(request, Request)
        if len(request.params) < 3:
            raise InvalidParams("method=register&x=y&z=w&moduleId=mid&sensorId=sid&sensorName=mysensor where x is product field, y is product string, z is serial field, is serial string")
        assert request.params.items()[0][0] == "method"
        assert request.params.items()[0][1] == "register"
        (product_name_field, product_name_string) = request.params.items()[1]
        (serial_number_field, serial_number_string) = request.params.items()[2]
        assert isinstance(product_name_field, str)
        product_name_field = unicode(product_name_field) 
        assert isinstance(product_name_field, unicode)
        assert isinstance(serial_number_field, str)
        serial_number_field = unicode(serial_number_field)
        assert isinstance(serial_number_string, unicode)
        try:
            product_name_data = Data.prepare(product_name_field, product_name_string)
            serial_number_data = Data.prepare(serial_number_field, serial_number_string)
            module_id_string = request.get("moduleId")
            assert len(module_id_string) > 0
            sensor_id_string = request.get("sensorId")
            assert len(sensor_id_string) > 0
            module_id_data = Data.prepare("moduleId", request.get("moduleId"))
            sensor_id_data = Data.prepare("sensorId", request.get("sensorId"))
            existing_sensor = Sensor.getByProductNameSerialNumberModuleIdSensorId(product_name_data, serial_number_data, module_id_data, sensor_id_data)
            raise EntityExists("Equipment", {product_name_field:product_name_string, serial_number_field: serial_number_string, "moduleId":module_id_string, "sensorId":sensor_id_string})
        except EntityNotFound: pass
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        sensor_name = request.get("sensorName")
        if len(sensor_name) == 0: sensor_name = unicode(sensor_name)
        sensor_name_data = Data.prepare("sensorName", sensor_name)
        sensor = Sensor.create(product_name_data, serial_number_data, module_id_data, sensor_id_data, sensor_name_data, odenki_user)
        jresponse.addResult(sensor)

class OneHour(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        pass

class Recent(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        pass
    
class Register(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        pass

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Sensor", Enumerate))
    mapping.append(("/api/Sensor/[0-9]+", Recent))
    mapping.append(("/api/Sensor/[0-9]+/[0-9][0-9][0-9][0-9]/[0-9]+/[0-9]+/[0-9]+", OneHour))
    mapping.append(("/api/Sensor/register", Register))
    run_wsgi_app(mapping)
