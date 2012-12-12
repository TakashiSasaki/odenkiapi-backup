#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.OdenkiUser import OdenkiUser
from model.EmailUser import EmailUser
from model.TwitterUser import TwitterUser
from model.GmailUser import GmailUser
from lib.gae import run_wsgi_app
from google.appengine.api import users
from gaesessions import get_current_session
import json

class Settings(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        
        try:
            odenki_user = OdenkiUser.loadFromSession()
            assert isinstance(odenki_user, OdenkiUser)
        except: odenki_user = None
        
        try:
            email_user = EmailUser.getByOdenkiId(odenki_user.odenkiId)
            assert isinstance(email_user, EmailUser)
        except: email_user = None
        
        try:
            twitter_user = TwitterUser.getByOdenkiId(odenki_user.odenkiId)
            assert isinstance(twitter_user, TwitterUser)
        except: twitter_user = None
        
        try:
            gmail_user = GmailUser.getByOdenkiId(odenki_user.odenkiId)
            assert isinstance(gmail_user, GmailUser)
        except: gmail_user = None
        
        jresponse.setResultValue(odenki_user.__class__.__name__, odenki_user)
        jresponse.setResultObject(email_user)
        jresponse.setResultObject(twitter_user)
        jresponse.setResultObject(gmail_user)
        login_url = users.create_login_url("/api/auth/Gmail/RedirectedFromGoogle")
        jresponse.setResultValue("login_url", login_url)

    def setAdmin(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        assert isinstance(jrequest, JsonRpcRequest)
        assert jrequest.fromAdminHost
        jresponse.setId()
        session = get_current_session()
        self._setAdminMode(True)
        for x in session:
            jresponse.setResultValue(x, session[x])
        
    def unsetAdmin(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        assert isinstance(jrequest, JsonRpcRequest)
        assert jrequest.fromAdminHost
        jresponse.setId()
        session = get_current_session()
        self._setAdminMode(False)
        for x in session:
            jresponse.setResultValue(x, session[x])

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/settings", Settings))
    run_wsgi_app(mapping)
