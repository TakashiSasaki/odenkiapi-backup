#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher, run_wsgi_app
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.EmailUser import EmailRegistration, EmailUser
from lib.json.JsonRpcError import JsonRpcError, JsonRpcException, InvalidParams, \
    UnexpectedState, EntityNotFound
from gaesessions import get_current_session
from logging import debug
import gaesessions

EMAIL_REGISTRATION_NONCE = str("f5464d0jVbvde1Uxtur")

class Email(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            email_user = EmailUser.loadFromSession()
            assert isinstance(email_user, EmailUser)
            jresponse.setResultValue("email", email_user.email)
            jresponse.setResultValue("emailUserId", email_user.emailUserId)
        except EntityNotFound:
            pass
        session = gaesessions.get_current_session()
        try:
            nonce = session[EMAIL_REGISTRATION_NONCE]
            jresponse.setResultValue("nonce", nonce)
        except KeyError:
            pass
        
    def startOver(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

    def setEmail(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            email = unicode(jrequest.getValue("email")[0])
        except Exception:
            raise JsonRpcException(None, "email is not given for setEmail method.")
        email_registration = EmailRegistration.createNew(email)
        assert isinstance(email_registration, EmailRegistration)
        jresponse.setResultValue("email", email_registration.email)
        jresponse.setResultValue("nonce", email_registration.nonce)
        jresponse.setResultValue("beginning", email_registration.beginning)
        
        from google.appengine.api import mail
        message = mail.EmailMessage()
        message.to = email
        message.body = "http://odenkiapi.appengine.com/api/Email/" + email_registration.nonce + " にアクセスして下さい。"
        message.sender = "admin@odenki.org"
        message.subject = "みんなでおでんきへの登録確認メール"
        message.send()
    
    def invalidateEmail(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        email_user = EmailUser.loadFromSession()
        if email_user is None:
            jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, "user is not logged in.")
        email_user.invalidate()

    def setPassword(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            session = gaesessions.get_current_session()
            nonce = session[EMAIL_REGISTRATION_NONCE]
        except Exception, e:
            raise UnexpectedState("Nonce is not stored in session data.")
        assert isinstance(nonce, unicode)
        email_user = EmailUser.getByNonce(nonce)
        assert isinstance(email_user, EmailUser)
        try:
            raw_password = jrequest.getValue("password")[0].decode()
            raw_password2 = jrequest.getValue("password2")[0].decode()
        except Exception, e:
            raise InvalidParams("setPassword method requires password and password2. %s" % e)
        if raw_password != raw_password2:
            jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, "two passwords do not match.")
            return
        email_user.setPassword(raw_password)
        email_user.saveToSession()
        assert isinstance(email_user.hashedPassword, unicode)
        jresponse.setResultValue("hashed_password", email_user.hashedPassword)

class SetNonce(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        nonce = unicode(jrequest.getPathInfo(3))
        session = gaesessions.get_current_session()
        session[EMAIL_REGISTRATION_NONCE] = nonce
        jresponse.setRedirectTarget("/html/auth/Email.html")

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Email/[a-zA-Z0-9-]+", SetNonce))
    mapping.append(("/api/Email", Email))
    run_wsgi_app(mapping)
