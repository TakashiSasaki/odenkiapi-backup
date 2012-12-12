from model.NdbModel import NdbModel
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityNotFound, EntityDuplicated, EntityExists
from gaesessions import get_current_session, Session


class Outlet(NdbModel):
    
    SESSION_KEY = "diuijlkanbfyiuguwrqxfc76tfkv"
    
    outletId = ndb.StringProperty()
    relayId = ndb.StringProperty()
    secret = ndb.StringProperty(indexed=False)
    outletName = ndb.StringProperty(indexed=False)
    cardId = ndb.StringProperty(indexed=False)
    cardType = ndb.StringProperty(indexed=False)
    odenkiId = ndb.IntegerProperty(indexed=False)
    lastTouched = ndb.DateTimeProperty(indexed=False)

    def saveToSession(self):
        session = get_current_session()
        assert isinstance(session, Session)
        session[self.SESSION_KEY] = self
            
    @classmethod
    def loadFromSession(cls):
        session = get_current_session()
        assert isinstance(session, Session)
        try:
            outlet = session[cls.SESSION_KEY]
            assert isinstance(outlet, Outlet)
            return outlet
        except KeyError:
            raise EntityNotFound("No Outlet in the session.")

    @classmethod
    def getByCard(cls, card_type, card_id):
        q = Outlet.query()
        q = q.filter(cls.cardId == card_id)
        q = q.filter(cls.cardType == card_type)
        keys = q.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound({"cardId": card_id, "cardType": card_type})
        if len(keys) >= 2:
            raise EntityDuplicated({"cardId":card_id, "cardType": card_type})
        return keys[0].get()

    @classmethod
    def getByOutletId(cls, outlet_id):
        assert isinstance(outlet_id, unicode)
        q = Outlet.query()
        q = q.filter(cls.outletId == outlet_id)        
        keys = q.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound({"outletId": outlet_id})
        if len(keys) >= 2:
            raise EntityNotFound({"outletId": outlet_id})
        return keys[0].get()

    @classmethod
    def create(self, outlet_id):
        try:
            outlet = Outlet.getByOutletId(outlet_id)
            assert isinstance(outlet, Outlet)
            raise EntityExists({"outletId":outlet_id})
        except: pass
        outlet = Outlet()
        outlet.outletId = outlet_id
        outlet.put()
        return outlet

