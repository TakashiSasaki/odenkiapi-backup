from __future__ import unicode_literals, print_function
from model.NdbModel import NdbModel
from google.appengine.ext import ndb
from lib.json.JsonRpcError import EntityNotFound, EntityExists
import gaesessions

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
    def queryByGmailId(cls, gmail_id):
        assert isinstance(gmail_id, str) #user_id() returns str, not unicode
        query = ndb.Query(kind="GmailUser")
        query = query.filter(cls.gmailId == gmail_id)
        return query
    
    @classmethod
    def keyByGmailId(cls, gmail_id):
        assert isinstance(gmail_id, str) #user_id() returns str, not unicode
        query = cls.queryByGmailId(gmail_id)
        key = query.get(keys_only=True)
        if key is None:
            raise EntityNotFound(cls, {"gmailId":gmail_id})
        assert isinstance(key, ndb.Key)
        return key
    
    @classmethod
    def getByGmailId(cls, gmail_id):
        assert isinstance(gmail_id, str) #user_id() returns str, not unicode
        key = cls.keyByGmailId(gmail_id)
        entity = key.get()
        assert isinstance(entity, cls)

    @classmethod
    def getByOdenkiId(cls, odenki_id):
        key = cls.keyByOdenkiId(odenki_id)
        entity = key.get()
        assert isinstance(entity, GmailUser)
        return entity
    
    @classmethod
    def keyByOdenkiId(cls, odenki_id):
        query = cls.queryByOdenkiId(odenki_id)
        key = query.get(keys_only=True)
        if key is None:
            raise EntityNotFound(cls, {"odenki_id": odenki_id})
        assert isinstance(key, ndb.Key)
        return key

    @classmethod
    def queryByOdenkiId(cls, odenki_id):
        query = ndb.Query(kind="GmailUser")
        query = query.filter(cls.odenkiId == odenki_id)
        assert isinstance(query, ndb.Query)
        return query
