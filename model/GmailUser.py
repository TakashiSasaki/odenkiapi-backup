#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from model.NdbModel import NdbModel
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityNotFound, EntityExists, EntityDuplicated
import gaesessions
from gaesessions import Session

class GmailUser(NdbModel):
    gmail = ndb.StringProperty(indexed=False)
    nickname = ndb.StringProperty(indexed=False)
    gmailId = ndb.StringProperty()
    odenkiId = ndb.IntegerProperty()
    
    SESSION_KEY = "qwzuw56ut7o0pgrw1zOrtU"

    @classmethod
    def loadFromSession(cls):
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        if not session.has_key(cls.SESSION_KEY):
            raise EntityNotFound(cls, {"in": "session"})
        gmail_user = session[cls.SESSION_KEY]
        assert isinstance(gmail_user, GmailUser)
        return gmail_user
    
    def saveToSession(self):
        """saves instance of GmailUser as session variable copying odenkiId from OdenkiUser instance in the session if exists."""
        try:
            existing = GmailUser.loadFromSession()
            assert isinstance(existing, GmailUser)
            if existing.gmailId != self.gmailId:
                raise EntityExists(self.__class__, {"existing.gmailId": existing.gmailId, "self.GmailId": self.gmailId})
        except EntityNotFound: pass
        session = gaesessions.get_current_session()
        session[self.SESSION_KEY] = self
        
    @classmethod    
    def deleteFromSession(cls):
        session = gaesessions.get_current_session()
        if __debug__: assert isinstance(session, Session)
        session.pop(cls.SESSION_KEY)
    
    @classmethod
    def queryByGmailId(cls, gmail_id):
        assert isinstance(gmail_id, str) #user_id() returns str, not unicode
        query = ndb.Query(kind="GmailUser")
        query = query.filter(cls.gmailId == gmail_id)
        return query
    
    @classmethod
    def keyByGmailId(cls, gmail_id):
        assert isinstance(gmail_id, str) #user_id() returns str, not unicode
        query = cls.queryByGmailId(gmail_id)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys == 0):
            raise EntityNotFound(cls, {"gmailId":gmail_id})
        if len(keys == 2):
            raise EntityDuplicated(cls, {"gmailId": gmail_id})
        return keys[0]
    
    @classmethod
    def getByGmailId(cls, gmail_id):
        assert isinstance(gmail_id, str) #user_id() returns str, not unicode
        return cls.keyByGmailId(gmail_id).get()

    @classmethod
    def getByOdenkiId(cls, odenki_id):
        return cls.keyByOdenkiId(odenki_id).get()
    
    @classmethod
    def keyByOdenkiId(cls, odenki_id):
        query = cls.queryByOdenkiId(odenki_id)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound(cls, {"odenki_id": odenki_id})
        if len(keys) == 2:
            raise EntityDuplicated(cls, {"odenki_id": odenki_id})
        return keys[0]

    @classmethod
    def queryByOdenkiId(cls, odenki_id):
        assert isinstance(odenki_id, int)
        query = ndb.Query(kind="GmailUser")
        query = query.filter(cls.odenkiId == odenki_id)
        assert isinstance(query, ndb.Query)
        return query
