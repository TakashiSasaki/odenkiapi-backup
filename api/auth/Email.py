#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher, run_wsgi_app
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.EmailUser import EmailUser, hashPassword
from lib.json.JsonRpcError import InvalidParams, EntityNotFound, PasswordMismatch, \
    InconsistentAuthentiation
from model.OdenkiUser import OdenkiUser
import re
from google.appengine.ext import ndb

class Email(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        
        odenki_user, email_user = None, None
        try:
            odenki_user = OdenkiUser.loadFromSession()
            assert isinstance(odenki_user, OdenkiUser)
            email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
            assert isinstance(email_user, EmailUser)
        except EntityNotFound: pass
        except AttributeError: pass

        jresponse.setResultValue("EmailUser", email_user)
        jresponse.setResultValue("OdenkiUser", odenki_user)
        jresponse.setResultValue("host", jrequest.request.host)
        
    def showAllEmailUsers(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        assert jrequest.fromAdminHost
        jresponse.setId()
        query = EmailUser.query()
        email_users = []
        for email_user in query:
            email_users.append(email_user)
        jresponse.setResult(email_users)

    def invalidate(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
        assert isinstance(email_user, EmailUser)
        email_user.invalidate()

    def setPassword(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
#        try:
#            session = gaesessions.get_current_session()
#            nonce = session[EMAIL_REGISTRATION_NONCE]
#        except Exception, e:
#            session.pop(EMAIL_REGISTRATION_NONCE);
#            raise UnexpectedState("Nonce is not stored in session data.")
#        assert isinstance(nonce, unicode)
#        email_user = EmailUser.getByNonce(nonce)
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound:
            odenki_user = None
        email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
        assert isinstance(email_user, EmailUser)
        try:
            raw_password = jrequest.getValue("password")[0].decode()
            raw_password2 = jrequest.getValue("password2")[0].decode()
            assert len(raw_password) < 8
        except Exception, e:
            raise InvalidParams("setPassword method requires password and password2. %s" % e)
        if raw_password != raw_password2:
            raise PasswordMismatch(hashPassword(raw_password), hashPassword(raw_password2))
        email_user.setPassword(raw_password)
        email_user.put()
        email_user.saveToSession()
        assert isinstance(email_user.hashedPassword, unicode)
        jresponse.setResult(email_user)
    
    def deleteEmailUser(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        odenki_user = OdenkiUser.loadFromSession()
        assert isinstance(odenki_user, OdenkiUser)
        email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
        email_user.key.delete_async()
#        email_user = EmailUser.loadFromSession()
#        assert isinstance(email_user, EmailUser)
#        key = email_user.key
#        from google.appengine.ext import ndb
#        assert isinstance(key, ndb.Key)
#        key.delete()
    
    def login(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            email = jrequest.getValue("email")[0]
            raw_password = jrequest.getValue("password")[0]
        except Exception:
            raise InvalidParams("email and password are required for method=login.")
        try:    
            email_user = EmailUser.getByEmail(email)
        except Exception:
            raise EntityNotFound("EmailUser entity is not found", {"email": email})
        assert isinstance(email_user, EmailUser)
        email_user.matchPassword(raw_password) # raises PasswordMismatch if password not matches
#        email_user.saveToSession()
        
        assert email_user.odenkiId is not None
        odenki_user = OdenkiUser.getByOdenkiId(email_user.odenkiId)
        odenki_user.saveToSession()
        EmailUser.deleteFromSession()
        
        jresponse.setResultValue("EmailUser", email_user)
        jresponse.setResultValue("OdenkiUser", odenki_user)
    
    def deleteNullOdenkiId(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        assert jrequest.fromAdminHost
        jresponse.setId()
        email_user_query = EmailUser.query()
        assert (email_user_query, ndb.Query)
        #email_user_query = email_user_query.filter(EmailUser.odenkiId==None)
        email_user_query = email_user_query.filter()
        count1 = 0
        for email_user_key in email_user_query.fetch(keys_only=True):
            assert isinstance(email_user_key, ndb.Key)
            if email_user_key.get().odenkiId is None:
                email_user_key.delete_async()
                count1 += 1
        jresponse.setResultValue("count1", count1)

        count2 = 0
        for email_user_key in email_user_query.fetch(keys_only=True):
            assert isinstance(email_user_key, ndb.Key)
            if email_user_key.get().odenkiId is None:
                email_user_key.delete_async()
                count2 += 1
        jresponse.setResultValue("count2", count2)

#    def logout(self, jrequest, jresponse):
#        jresponse.setId()
#        session = gaesessions.get_current_session()
#        session.terminate()
#        email_user = None
#        try:
#            email_user = EmailUser.loadFromSession()
#        except EntityNotFound: pass
#        odenki_user = None
#        try:
#            odenki_user = OdenkiUser.loadFromSession()
#        except EntityNotFound: pass
#        jresponse.setResult({"OdenkiUser": odenki_user, "EmailUser": email_user})

class SetNonce(JsonRpcDispatcher):

    def POST(self, jrequest, jresponse):
        """generate a nonce with given password and send the corresponding URL to the user.
        This round trip is intended to associate a password to an email address.
        """
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            email = unicode(jrequest.getValue("email")[0])
            raw_password = jrequest.getValue("password")[0].decode()
            raw_password2 = jrequest.getValue("password2")[0].decode()
        except TypeError:
            raise InvalidParams(message="email, password and password2 were mandatory.")
        
        if len(raw_password) < 8:
            raise InvalidParams(message="password should be eight characters or more")
        if raw_password != raw_password2:
            raise PasswordMismatch()
        match = re.search(r'^[\w.-\\\\+]+@[\w.-]+$', email)
        if not match:
            raise InvalidParams({"email": email}, "Malformed email '%s' address was given." % email)
        
        #email_user = None
        # check if OdenkiUser is loaded 
#        try: 
#            odenki_user = OdenkiUser.loadFromSession()
#            email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
#        except EntityNotFound: pass 

        # check if EmailUser already exists.

        try: 
            email_user = EmailUser.getByEmail(email)
        except EntityNotFound:
            email_user = EmailUser.createByEmail(email)
        assert isinstance(email_user, EmailUser)
        email_user.setNonce(email, raw_password)
        #EmailUser.deleteFromSession()
        
        from google.appengine.api import mail
        message = mail.EmailMessage()
        message.to = email
        message.body = "「みんなでおでんき」に関心をお持ちいただきありがとうございます。\n" + \
            ("このメールアドレス %s" % email) + " でご登録いただくには次のページを開いて下さい。 \n " + \
            ("http://%s/api/Email/%s" % (jrequest.request.host, email_user.nonce)) + "\n" + \
            "みんなでおでんきに登録しない場合はこのメールを無視して下さい。\n"
        message.sender = "admin@odenki.org"
        message.subject = "みんなでおでんきへの登録確認メール"
        message.send()
        jresponse.setResultValue("EmailUser", email_user)
        jresponse.setResultValue("email", email)
    

class NonceCallback(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        """load EmailUser instance by nonce.
        Nonce will be invalidated and email will be updated."""
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        #EmailUser.deleteFromSession()
        nonce = unicode(jrequest.getPathInfo(4))
        email_user = EmailUser.getByNonce(nonce)
        assert isinstance(email_user, EmailUser)
        assert email_user.nonceEmail is not None
        email_user.email = email_user.nonceEmail
        email_user.nonceEmail = None
        email_user.hashedPassword = email_user.nonceHashedPassword
        email_user.nonceHashedPassword = None
        email_user.nonce = None
        email_user.put_async()
        #email_user.saveToSession()
        
        # prepare OdenkiUser
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound:
            odenki_user = None
            
        # reconcile EmailUser and OdenkiUser
        if odenki_user is None:
            if email_user.odenkiId is None:
                odenki_user = OdenkiUser.createNew()
                assert isinstance(odenki_user, OdenkiUser)
                odenki_user.saveToSession()
                email_user.setOdenkiId(odenki_user.odenkiId)
                email_user.put_async()
            else:
                odenki_user = OdenkiUser.getByOdenkiId(email_user.odenkiId)
                odenki_user.saveToSession()
        else:
            if email_user.odenkiId is None:
                odenki_user.saveToSession()
                email_user.setOdenkiId(odenki_user.odenkiId)
                email_user.put_async()
            else:
                if email_user.odenkiId != odenki_user.odenkiId:
                    raise InconsistentAuthentiation({email_user.__class__.__name__: email_user,
                                                     odenki_user.__class__.__name__:odenki_user})
                odenki_user.saveToSession()
        
        jresponse.setResultValue(odenki_user.__class__.__name__, odenki_user)
        jresponse.setResultValue(email_user.__class__.__name__, email_user)
        #jresponse.setResultValue("nonce", nonce)
        jresponse.setRedirectTarget("http://%s/html/auth/Email.html" % jrequest.request.host)

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/auth/Email/setNonce", SetNonce))
    mapping.append(("/api/auth/Email/[a-zA-Z0-9-]+", NonceCallback))
    mapping.append(("/api/auth/Email", Email))
    run_wsgi_app(mapping)
