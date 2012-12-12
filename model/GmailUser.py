#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from model.NdbModel import NdbModel
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityNotFound, EntityExists, EntityDuplicated
import gaesessions
from gaesessions import Session
#from model.OdenkiUser import OdenkiUser

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
        assert isinstance(keys, list)
        if len(keys) == 0:
            raise EntityNotFound({"kind": cls.__name__ , "gmailId":gmail_id})
        if len(keys) == 2:
            gmail_user_1 = keys[0].get()
            assert isinstance(gmail_user_1, GmailUser)
            gmail_user_2 = keys[1].get()
            assert isinstance(gmail_user_2, GmailUser)
            if gmail_user_1.odenkiId == gmail_user_2.odenkiId:
                gmail_user_2.key.delete_async()
                return gmail_user_1.key
            raise EntityDuplicated({"gmail_user_1": gmail_user_1, "gmail_user_2": gmail_user_2,
                                    "gmailId":gmail_id})
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
            raise EntityNotFound({"kind": cls.__name__,
                                  "odenkiId": odenki_id})
        if len(keys) == 2:
            gmail_user_1 = keys[0].get()
            assert isinstance(gmail_user_1, GmailUser)
            gmail_user_2 = keys[1].get()
            assert isinstance(gmail_user_2, GmailUser)
            if gmail_user_1.gmailId == gmail_user_2.gmailId:
                gmail_user_2.key.delete_async()
                return gmail_user_1.key
            raise EntityDuplicated({"odenkiId": odenki_id,
                                    "gmail_user_1": gmail_user_1,
                                    "gmail_user_2": gmail_user_2})
        return keys[0]

    @classmethod
    def queryByOdenkiId(cls, odenki_id):
        assert isinstance(odenki_id, int)
        query = ndb.Query(kind="GmailUser")
        query = query.filter(cls.odenkiId == odenki_id)
        assert isinstance(query, ndb.Query)
        return query

    def setOdenkiId(self, odenki_id):
        assert odenki_id is not None
        assert self.odenkiId is None
        
        try:
            existing_gmail_user = GmailUser.getByOdenkiId(odenki_id)
            raise EntityExists({"ExistingGmailUser" : existing_gmail_user,
                                "IncomingGmailUser": self,
                                "odenkiId": odenki_id})
        except EntityNotFound: pass

        self.odenkiId = odenki_id
        self.put_async()
        
    @classmethod
    def deleteAll(cls):
        query = ndb.Query()
        for x in query.fetch(keys_only=True):
            assert isinstance(x, ndb.Key)
            x.delete_async()
