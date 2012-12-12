#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.OdenkiUser import OdenkiUser
from lib.gae import run_wsgi_app
from lib.json.JsonRpcError import EntityNotFound
from model.Outlet import Outlet

class Settings(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        
        try:
            odenki_user = OdenkiUser.loadFromSession()
            assert isinstance(odenki_user, OdenkiUser)
        except: odenki_user = None
        
        try:
            outlet = Outlet.loadFromSession()
            assert isinstance(outlet, Outlet)
        except EntityNotFound: 
            outlet = None
        jresponse.setResultObject(odenki_user)
        jresponse.setResultObject(outlet)


if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/outlet/status", Settings))
    run_wsgi_app(mapping)
