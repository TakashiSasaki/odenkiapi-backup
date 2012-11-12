#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from model.NdbModel import NdbModel
from google.appengine.ext import ndb
from model.Counter import Counter
from uuid import uuid4, UUID
from hashlib import sha1
from datetime import datetime
from lib.json.JsonRpcError import EntityNotFound, EntityExists, PasswordMismatch, EntityDuplicated
from logging import debug
import gaesessions
from model.OdenkiUser import OdenkiUser
#from gaesessions import Session

def _hashPassword(raw_password):
    assert isinstance(raw_password, unicode)
    PASSWORD_SALT = "llj5fpioifht0;iu"
    password_with_salt = PASSWORD_SALT + raw_password
    s = sha1()
    s.update(password_with_salt)
    hashed_password = s.hexdigest()
    assert isinstance(hashed_password, str)
    return hashed_password

class EmailUser(NdbModel):
    
    emailUserId = ndb.IntegerProperty()
    email = ndb.StringProperty()
    nonceEmail = ndb.StringProperty(indexed=False)
    hashedPassword = ndb.StringProperty(indexed=False)
    registeredDateTime = ndb.DateTimeProperty(indexed=False)
    invalidatedDateTime = ndb.DateTimeProperty()
    odenkiId = ndb.IntegerProperty()
    nonce = ndb.StringProperty()
    nonceDateTime = ndb.DateTimeProperty(indexed=False)
    lastFail = ndb.DateTimeProperty(indexed=False)
    failCount = ndb.IntegerProperty(indexed=False)
    
    def matchPassword(self, raw_password):
        assert isinstance(raw_password, unicode)
        hashed_password = _hashPassword(raw_password)
        debug("given password = %s, given hashed password = %s, stored hashed password = %s" % (raw_password, hashed_password, self.hashedPassword))
        if hashed_password != self.hashedPassword:
            raise PasswordMismatch(hashed_password)

    @ndb.toplevel
    def setPassword(self, raw_password):
        assert isinstance(raw_password, unicode)
        hashed_password = _hashPassword(raw_password)
        assert len(hashed_password) == 40
        debug("hashed_password=%s" % hashed_password)
        self.hashedPassword = hashed_password
        self.put()
        

    @classmethod
    def getByEmail(cls, email):
        assert isinstance(email, unicode)
        query = ndb.Query(kind="EmailUser")
        query = query.filter(cls.email == email)
        query = query.filter(cls.invalidatedDateTime == None)
        keys = query.fetch(limit=2, keys_only=True)
        if len(keys) == 2:
            raise EntityDuplicated({"email":email})
        if len(keys) == 0:
            raise EntityNotFound(cls, {"email":email})
        return keys[0].get()
        return 
    
    @classmethod
    def getByEmailUserId(cls, email_user_id):
        assert isinstance(email_user_id, int)
        query = ndb.Query(kind="EmailUser")
        query = query.filter(cls.emailUserId == email_user_id)
        query = query.filter(cls.invalidatedDateTime == None)
        keys = query.fetch(limit=2, keys_only=True)
        if len(keys) == 0:
            raise EntityNotFound(cls, {"emailUserId": email_user_id})
        if len(keys) == 2:
            raise EntityDuplicated(cls, {"emailUserId": email_user_id})
        return keys[0].get()
    
    @classmethod
    def createByEmail(cls, email):
        assert isinstance(email, unicode)
        try:
            existing_email_user = cls.getByEmail(email)
            raise EntityExists(cls, {"existing_email_user": existing_email_user})
        except: pass
        email_user = EmailUser()
        assert isinstance(email_user, EmailUser)
        email_user.email = email
        email_user.registeredDateTime = datetime.now()
        email_user.emailUserId = Counter.GetNextId("emailUserId")
        odenki_user = OdenkiUser.createNew()
        assert isinstance(odenki_user, OdenkiUser)
        email_user.odenkiId = odenki_user.odenkiId
        email_user.put()
        return email_user

    def invalidate(self):
        """TODO: It should not be deleted but invalidated."""
        self.invalidatedDateTime = datetime.now()
        self.put()
        
    SESSION_KEY = "nasfuafhasjlafapsiofhap"

    @classmethod    
    def loadFromSession(cls):
        """get EmailUser instance in the session"""
        from gaesessions import get_current_session
        session = get_current_session()
        try:
            email_user = session[cls.SESSION_KEY]
        except KeyError:
            raise EntityNotFound(cls, "loadFromSession")
        if email_user is None:
            raise EntityNotFound(cls, "loadFromSession")
        assert isinstance(email_user, EmailUser)
        return email_user
        
    def saveToSession(self):
        assert isinstance(self.key, ndb.Key)
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        try:
            existing = self.loadFromSession()
            assert isinstance(existing, EmailUser)
            if existing.emailUserId != self.emailUserId:
                raise EntityExists(self.__class__, {"existing.emailUserId": existing.emailUserId, "self.emailUserId": self.emailUserId})
        except EntityNotFound: pass
        session[self.SESSION_KEY] = self
        
    @classmethod
    def deleteFromSession(cls):
        """delete EmailUser instance from the session"""
        from gaesessions import get_current_session
        session = get_current_session()
        assert isinstance(session, gaesessions.Session)
        session.pop(cls.SESSION_KEY)

    @classmethod
    def getByNonce(cls, nonce):
        assert isinstance(nonce, unicode)
        query = ndb.Query(kind="EmailUser")
        query = query.filter(cls.nonce == nonce)
        query = query.filter(cls.invalidatedDateTime == None)
        keys = query.fetch(limit=2, keys_only=True)
        if len(keys) == 2:
            raise EntityDuplicated(cls, {"nonce" : nonce})
        if len(keys) == 0:
            raise EntityNotFound(cls, {"nonce": nonce})
        return keys[0].get()
    
    def setNonce(self, nonce_email):
        uuid = uuid4()
        assert isinstance(uuid, UUID)
        nonce = uuid.get_hex().decode()
        assert isinstance(nonce, unicode)
        self.nonce = nonce
        self.nonceDateTime = datetime.utcnow()
        self.nonceEmail = nonce_email
        self.put()

    @classmethod
    def getByOdenkiId(cls, odenki_id):
        return cls.keyByOdenkiId(odenki_id).get()

    @classmethod
    def keyByOdenkiId(cls, odenki_id):
        query = cls.queryByOdenkiId(odenki_id)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            raise EntityNotFound(cls, {"odenkiId": odenki_id})
        if len(keys) == 2:
            raise EntityDuplicated(cls, {"odenkiId:": odenki_id})
        return keys[0]
    
    @classmethod
    def queryByOdenkiId(cls, odenki_id):
        query = ndb.Query(kind="EmailUser")
        query = query.filter(cls.invalidatedDateTime == None)
        query = query.filter(cls.odenkiId == odenki_id)
        return query
