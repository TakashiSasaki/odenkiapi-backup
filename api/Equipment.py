#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from google.appengine.ext import ndb
from model.Equipment import Equipment
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
        query = ndb.Query("Equipment")
        query = query.order(-Equipment.equipmentId)
        keys = query.fetch(keys_only=True, limit=100)
        for key in keys:
            jresponse.addResult(key.get())
            
    def register(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        request = jrequest.request
        assert isinstance(request, Request)
        if len(request.params) != 3:
            raise InvalidParams("method=register&x=y&z=w where x is product field, y is product string, z is serial field, is serial string")
        assert request.params.items()[0][0] == "method"
        assert request.params.items()[0][1] == "register"
        (product_field, product_string) = request.params.items()[1]
        (serial_field, serial_string) = request.params.items()[2]
        assert isinstance(product_field, str)
        product_field = unicode(product_field) 
        assert isinstance(product_string, unicode)
        assert isinstance(serial_field, str)
        serial_field = unicode(serial_field)
        assert isinstance(serial_string, unicode)
        try:
            product_data = Data.getByFieldAndString(unicode(product_field), unicode(product_string))
            product = product_data.dataId
            serial_data = Data.getByFieldAndString(unicode(serial_field), unicode(serial_string))
            serial = serial_data.dataId
            existing_equipment = Equipment.getByProductAndSerial(product, serial)
            raise EntityExists("Equipment", {product_field:product_string, serial_field: serial_string})
        except EntityNotFound: pass
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        equipment = Equipment.create(odenki_user.odenkiId, product_field, product_string, serial_field, serial_string)
        jresponse.addResult(equipment)

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
    mapping.append(("/api/Equipment", Enumerate))
    mapping.append(("/api/Equipment/[0-9]+", Recent))
    mapping.append(("/api/Equipment/[0-9]+/[0-9][0-9][0-9][0-9]/[0-9]+/[0-9]+/[0-9]+", OneHour))
    mapping.append(("/api/Equipment/register", Register))
    run_wsgi_app(mapping)
