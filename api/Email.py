#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher, run_wsgi_app
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.EmailUser import EmailUser
from lib.json.JsonRpcError import JsonRpcError, JsonRpcException, InvalidParams, \
    UnexpectedState, EntityNotFound, PasswordMismatch
from logging import debug
import gaesessions
from model.OdenkiUser import OdenkiUser
from lib.Session import fillUser, fillEmailUser

#EMAIL_REGISTRATION_NONCE = str("f5464d0jVbvde1Uxtur")

class Email(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            email_user = EmailUser.loadFromSession()
        except EntityNotFound, e:
            email_user = None
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound, e:
            odenki_user = None
        jresponse.setResult({"EmailUser": email_user, "OdenkiUser":odenki_user})
        
#    def startOver(self, jrequest, jresponse):
#        assert isinstance(jrequest, JsonRpcRequest)
#        assert isinstance(jresponse, JsonRpcResponse)
#        jresponse.setId()
#
#        session = gaesessions.get_current_session()
#        assert isinstance(session, gaesessions.Session)
#        session.terminate()

    def setNonce(self, jrequest, jresponse):
        """If EmailUser is loaded into the session,
        it means the EmailUser is in some transitional state.
        Usually EmailUser is not loaded in the session and only OdenkiUser is loaded."""
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            email = unicode(jrequest.getValue("email")[0])
        except Exception:
            raise JsonRpcException(None, "email is not given for setEmail method.")
        
        email_user = None
        try:
            odenki_user = OdenkiUser.loadFromSession()
            email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
        except EntityNotFound, e: pass 

        if email_user is None:
            try: 
                email_user = EmailUser.getByEmail(email)
            except EntityNotFound, e: pass
        
        if email_user is None:
            email_user = EmailUser.createByEmail(email)

        assert isinstance(email_user, EmailUser)
        email_user.setNonce(email)
        EmailUser.deleteFromSession()
        
        from google.appengine.api import mail
        message = mail.EmailMessage()
        message.to = email
        message.body = "「みんなでおでんき」に関心をお持ちいただきありがとうございます。\n" + \
            ("このメールアドレス %s" % email) + " でご登録いただくには次のページを開いて下さい。 \n " + \
            ("http://odenkiapi.appspot.com/api/Email/%s" % email_user.nonce) + "\n" + \
            "みんなでおでんきに登録しない場合はこのメールを無視して下さい。\n"
        message.sender = "admin@odenki.org"
        message.subject = "みんなでおでんきへの登録確認メール"
        message.send()
        jresponse.setResult(email_user)
    
    def invalidate(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        email_user = EmailUser.loadFromSession()
        if email_user is None:
            jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, "user is not logged in.")
        email_user.invalidate()
        email_user.deleteFromSession()

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
        email_user = EmailUser.loadFromSession()
        assert isinstance(email_user, EmailUser)
        try:
            raw_password = jrequest.getValue("password")[0].decode()
            raw_password2 = jrequest.getValue("password2")[0].decode()
        except Exception, e:
            raise InvalidParams("setPassword method requires password and password2. %s" % e)
        if raw_password != raw_password2:
            raise PasswordMismatch(raw_password, raw_password2)
        email_user.setPassword(raw_password)
        email_user.put()
        email_user.saveToSession()
        assert isinstance(email_user.hashedPassword, unicode)
        #jresponse.setResultValue("hashed_password", email_user.hashedPassword)
#        jresponse.setResultValue("email", email_user.email)
#        jresponse.setResultValue("emailUserId", email_user.emailUserId)
#        jresponse.setResultValue("odenkiId", email_user.odenkiId)
        jresponse.setResult(email_user)
    
    def deleteEmail(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        email_user = EmailUser.loadFromSession()
        assert isinstance(email_user, EmailUser)
        key = email_user.key
        from google.appengine.ext import ndb
        assert isinstance(key, ndb.Key)
        key.delete()
    
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
        
#        fillUser()
        
#        try:
#            odenki_user = OdenkiUser.loadFromSession()
#        except EntityNotFound, e:
#            odenki_user = OdenkiUser.createNew()
#            odenki_user.saveToSession()
#            fillUser()
#        assert isinstance(OdenkiUser.loadFromSession(), OdenkiUser)
#        assert isinstance(EmailUser.loadFromSession(), EmailUser)
#        assert odenki_user.odenkiId == email_user.odenkiId
#        jresponse.setResultValue("email", email_user.email)
#        jresponse.setResultValue("emailUserId", email_user.emailUserId)
#        jresponse.setResultValue("odenkiId", email_user.odenkiId)
        jresponse.setResult([email_user, odenki_user])
        
    def logout(self, jrequest, jresponse):
        jresponse.setId()
        session = gaesessions.get_current_session()
        session.terminate()
        email_user = None
        try:
            email_user = EmailUser.loadFromSession()
        except EntityNotFound, e: pass
        odenki_user = None
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound, e: pass
        jresponse.setResult({"OdenkiUser": odenki_user, "EmailUser": email_user})

class NonceCallback(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        """load EmailUser instance by nonce.
        Nonce will be invalidated and email will be updated."""
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        EmailUser.deleteFromSession()
        jresponse.setRedirectTarget("http://odenki.org/html/auth/Email.html")
        nonce = unicode(jrequest.getPathInfo(3))
        email_user = EmailUser.getByNonce(nonce)
        assert isinstance(email_user, EmailUser)
        email_user.email = email_user.nonceEmail
        email_user.nonceEmail = None
        email_user.nonce = None
        email_user.put()
        email_user.saveToSession()

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Email/[a-zA-Z0-9-]+", NonceCallback))
    mapping.append(("/api/Email", Email))
    run_wsgi_app(mapping)
