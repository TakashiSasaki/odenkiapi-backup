#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from datetime import datetime
from model.Counter import  Counter
from google.appengine.ext import ndb
from model.NdbModel import NdbModel
import gaesessions
from lib.json.JsonRpcError import EntityNotFound, EntityExists, EntityDuplicated
from gaesessions import Session

class OdenkiUser(NdbModel):
    odenkiId = ndb.IntegerProperty(required=True)
    odenkiName = ndb.StringProperty(required=True, indexed=False)
    createdDateTime = ndb.DateTimeProperty(required=True, indexed=False)
    invalidatedDateTime = ndb.DateTimeProperty()
    
    SESSION_KEY = "rgznkwbIBUTIdrvcy"

    def saveToSession(self):
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        try:
            existing = self.loadFromSession()
            assert isinstance(existing, OdenkiUser)
            if existing.odenkiId != self.odenkiId:
                raise EntityExists({"OdenkiUserInSession": existing, "IncomingOdenkiUser": self})
        except EntityNotFound: pass
        session[self.SESSION_KEY] = self
    
    @classmethod
    def loadFromSession(cls):
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        if not session.has_key(cls.SESSION_KEY):
            raise EntityNotFound(message="OdenkiUser is not in the session.")
        odenki_user = session[cls.SESSION_KEY]
        assert isinstance(odenki_user, OdenkiUser)
        return odenki_user
    
    @classmethod
    def deleteFromSession(cls):
        session = gaesessions.get_current_session()
        assert isinstance(session, Session)
        session.pop(cls.SESSION_KEY)
    
    @classmethod
    def createNew(cls):
        """create new OdenkiUser with new odenkiId and put it to datastore"""
        odenki_user = OdenkiUser()
        odenki_user.odenkiId = Counter.GetNextId("odenkiId")
        odenki_user.odenkiName = "Odenki %s" % odenki_user.odenkiId
        odenki_user.createdDateTime = datetime.now()
        key = odenki_user.put()
        assert isinstance(key, ndb.Key)
        entity = key.get()
        assert isinstance(entity, OdenkiUser)
        return entity
    
    def setOdenkiName(self, new_odenki_name):
        assert isinstance(new_odenki_name, unicode)
        self.odenkiName = new_odenki_name
        self.put_async()

    @classmethod
    def queryByOdenkiId(cls, odenki_id):
        assert isinstance(odenki_id, int)
        query = ndb.Query(kind="OdenkiUser")
        query = query.filter(cls.odenkiId == odenki_id)
        query = query.filter(cls.invalidatedDateTime == None)
        return query
    
    @classmethod
    def keyByOdenkiId(cls, odenki_id):
        assert isinstance(odenki_id, int)
        query = cls.queryByOdenkiId(odenki_id)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound({"odenkiId": odenki_id}, "OdenkiUser.keyByOdenkiId")
        if len(keys) == 2:
            raise EntityDuplicated({"odenkiId":odenki_id}, "OdenkiUser.keyByOdenkiId")
        return keys[0]
    
    @classmethod
    def getByOdenkiId(cls, odenki_id):
        return cls.keyByOdenkiId(odenki_id).get()
