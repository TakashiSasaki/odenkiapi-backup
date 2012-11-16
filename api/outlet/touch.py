from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.Outlet import Outlet
from lib.json.JsonRpcError import EntityNotFound, InvalidParams
from lib.gae import run_wsgi_app
from model.OdenkiUser import OdenkiUser

class _Touch(JsonRpcDispatcher):

    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        
        outlet_id = None
        card_id = None
        try:
            outlet_id = unicode(jrequest.getValue("outletId")[0])
            assert isinstance(outlet_id, unicode)
            card_id = unicode(jrequest.getValue("cardId")[0])
            assert isinstance(card_id, unicode)
            card_type = unicode(jrequest.getValue("cardType")[0])
            assert isinstance(card_id, unicode)
        except Exception, e:
            raise InvalidParams({"outletId":None, "cardId":None, "exception": e.__class__.__name__})
        
        try:
            outlet = Outlet.getByOutletId(outlet_id)
        except EntityNotFound: 
            outlet = Outlet.create(outlet_id)
        assert isinstance(outlet, Outlet)
        outlet.cardId = card_id
        outlet.cardType = card_type
        outlet.put_async()
        
        try:
            outlet_name = jrequest.getValue("outletName")[0]
            assert isinstance(outlet_name, unicode)
            outlet.outletName = outlet_name
            outlet.put_async()
        except: pass
        
        try:
            odenki_user = OdenkiUser.loadFromSession()
            outlet.odenkiId = odenki_user.odenkiId
            outlet.put_async()
        except: pass
        
        outlet.saveToSession()
        
        jresponse.setResultObject(outlet)
        jresponse.setRedirectTarget("/html/outlet.html")

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/outlet/touch", _Touch))
    run_wsgi_app(mapping)
