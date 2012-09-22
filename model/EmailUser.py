from __future__ import unicode_literals, print_function
from model.NdbModel import NdbModel
from google.appengine.ext import ndb
from model.Counter import Counter
from uuid import uuid4, UUID
from hashlib import sha1
from datetime import datetime
from lib.json.JsonRpcError import JsonRpcException, EntityNotFound, EntityExists
from logging import debug
import gaesessions

def _hashPassword(raw_password):
    assert isinstance(raw_password, unicode)
    PASSWORD_SALT = "llj5fpioifht0;iu"
    password_with_salt = PASSWORD_SALT + raw_password
    s = sha1()
    s.update(password_with_salt)
    hashed_password = s.hexdigest()
    assert isinstance(hashed_password, str)
    return hashed_password

class EmailRegistration(NdbModel):
    
    emailUserId = ndb.IntegerProperty(indexed=False)
    #registrationId = ndb.IntegerProperty()
    email = ndb.StringProperty()
    nonce = ndb.StringProperty()
    beginning = ndb.DateTimeProperty(indexed=False)
    
    @classmethod
    def createNew(cls, email):
        assert isinstance(email, unicode)
        email_registration = EmailRegistration()
        email_registration.email = email
        assert isinstance(email_registration, EmailRegistration)
        try:
            email_user = EmailUser.loadFromSession()
            assert isinstance(email_user, EmailUser)
            email_registration.emailUserId = email_user.emailUserId
        except EntityNotFound:
            try:
                email_user = EmailUser.getByEmail(email)
                email_registration.emailUserId = email_user.emailUserId
            except EntityNotFound:
                pass
        cls.deleteOld(email)
        uuid = uuid4()
        assert isinstance(uuid, UUID)
        nonce = uuid.get_hex().decode()
        assert isinstance(nonce, unicode)
        email_registration.nonce = nonce
        debug("nonce = %s" % email_registration.nonce)
        email_registration.beginning = datetime.utcnow()
        key = email_registration.put()
        x = EmailRegistration.getByNonce(nonce)
        assert x.nonce == nonce
        assert isinstance(key, ndb.Key)
        return key.get()
    
    @classmethod
    def deleteOld(cls, email):
        assert isinstance(email, unicode)
        query = cls.query()
        assert isinstance(query, ndb.Query)
        query = query.filter(cls.email == email)
        keys = query.fetch(keys_only=True)
        for key in keys:
            key.delete()


    @classmethod
    def getByNonce(cls, nonce):
        assert isinstance(nonce, unicode)
        key = cls.keyByNonce(nonce)
        assert isinstance(key, ndb.Key)
        entity = key.get()
        assert isinstance(entity, EmailRegistration)
        return entity
    
    @classmethod
    def keyByNonce(cls, nonce):
        assert isinstance(nonce, unicode)
        query = cls.queryByNonce(nonce)
        key = query.get(keys_only=True)
        if key is None:
            raise EntityNotFound(cls, {"nonce": nonce})
        return key

    @classmethod
    def fetchByNonce(cls, nonce):
        assert isinstance(nonce, unicode)
        query = cls.queryByNonce(nonce)
        keys = query.fetch(keys_only=True)
        return keys

    @classmethod
    def queryByNonce(cls, nonce):
        assert isinstance(nonce, unicode)
        query = ndb.Query(kind="EmailRegistration")
        query = query.filter(cls.nonce == nonce)
        return query

    @classmethod
    def deleteByNonce(cls, nonce):
        assert isinstance(nonce, unicode)
        keys = cls.fetchByNonce(nonce)
        for key in keys:
            assert isinstance(key, ndb.Key)
            key.delete()

class EmailUser(NdbModel):
    
    emailUserId = ndb.IntegerProperty()
    email = ndb.StringProperty()
    hashedPassword = ndb.StringProperty(indexed=False)
    registeredDateTime = ndb.DateTimeProperty()
    
    def matchPassword(self, raw_password):
        assert isinstance(raw_password, unicode)
        hashed_password = _hashPassword(raw_password)
        return hashed_password == self.hashedPassword

    @ndb.toplevel
    def setPassword(self, raw_password):
        assert isinstance(raw_password, unicode)
        self.hashedPassword = _hashPassword(raw_password)
        self.put()
        

    @classmethod
    def getByEmail(cls, email):
        assert isinstance(email, unicode)
        query = ndb.Query(kind="EmailUser")
        query = query.filter(cls.email == email)
        entity = query.get()
        if entity is None:
            raise EntityNotFound(cls, {"email":email})
        return entity
    
    @classmethod
    def getByEmailUserId(cls, email_user_id):
        assert isinstance(email_user_id, int)
        query = ndb.Query(kind="EmailUser")
        query = query.filter(cls.emailUserId == email_user_id)
        entity = query.get()
        if entity is None:
            raise EntityNotFound(cls, {"emailUserId": email_user_id})
        return entity
    
    @classmethod
    def createByEmail(cls, email):
        assert isinstance(email, unicode)
        try:
            existing_email_user = cls.getByEmail(email)
            raise EntityExists(cls, {"existing_email_user": existing_email_user})
        except:
            pass
        email_user = EmailUser()
        assert isinstance(email_user, EmailUser)
        email_user.email = email
        email_user.registeredDateTime = datetime.now()
        email_user.emailUserId = Counter.GetNextId("emailUserId")
        email_user.put()
        return email_user

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
        session[self.SESSION_KEY] = self

    @classmethod
    def getByNonce(cls, nonce):
        assert isinstance(nonce, unicode)
        email_registration = EmailRegistration.getByNonce(nonce)
        debug(type(email_registration.email))
        assert isinstance(email_registration, EmailRegistration)
        if email_registration.emailUserId:
            email_user = EmailUser.getByEmailUserId(email_registration.emailUserId)
        else:
            email_user = EmailUser.createByEmail(email_registration.email)
        assert isinstance(email_user, EmailUser)
        return email_user
