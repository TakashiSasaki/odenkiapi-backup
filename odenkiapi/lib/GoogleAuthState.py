from __future__ import unicode_literals
from gaesessions import get_current_session, Session
from gdata.gauth import AeLoad, AeSave, AeDelete
from gdata.gauth import OAuthHmacToken, ACCESS_TOKEN, AUTHORIZED_REQUEST_TOKEN, REQUEST_TOKEN
from logging import debug
from lib.JsonEncoder import dumps

class NoGaeSessionException(RuntimeError):
    def __init__(self, message):
        RuntimeError.__init__(message)

class GoogleAuthSession(dict):

    def __init__(self):
        self.gaesession = get_current_session()
        if self.gaesession is None:
            raise NoGaeSessionException()
        assert isinstance(self.gaesession, Session)
        self._TOKEN_KEY = self.gaesession.sid + "_GoogleAuthSession"
        assert isinstance(self._TOKEN_KEY, unicode)
        assert self._isJsonizable()
        self._loadFromGaeSession()
        assert self._isJsonizable()

    def _loadFromGaeSession(self):
        existing_google_auth_session = self.gaesession.get("googleAuthSession")
        if existing_google_auth_session:
            debug("before update %s" % dumps(self))
            debug("existing keys %s" % existing_google_auth_session.keys())
            debug("existing %s" % dumps(existing_google_auth_session))
            assert isinstance(existing_google_auth_session, GoogleAuthSession)
            self.update(existing_google_auth_session)
            debug("after update %s" % dumps(self))
    
    def _saveToGaeSession(self):
        assert isinstance(self.gaesession, Session)
        assert self._isJsonizable()
        self.gaesession["googleAuthSession"] = self
        
    def _deleteFromGaeSession(self):
        assert isinstance(self.gaesession, Session)
        self.gaesession.de

    def _getToken(self):
        token = AeLoad(self._TOKEN_KEY)
        if token:
            assert isinstance(token, OAuthHmacToken)
            return token

    def _setToken(self, token):
        assert self._isJsonizable()
        assert isinstance(token, OAuthHmacToken)
        assert isinstance(self._TOKEN_KEY, unicode)
        self._saveToGaeSession()
        return AeSave(token, self._TOKEN_KEY)
    
    def _delToken(self):
        assert self._isJsonizable()
        AeDelete(self._TOKEN_KEY)
        self.clear()
        self._saveToGaeSession()
        assert AeLoad(self._TOKEN_KEY) is None
    
    def setNonAuthorizedRequestToken(self, non_authorized_request_token):
        assert isinstance(non_authorized_request_token, OAuthHmacToken)
        assert non_authorized_request_token.auth_state == REQUEST_TOKEN
        assert not self._getToken()
        self._setToken(non_authorized_request_token)
        self["nonAuthorizedRequestToken"] = non_authorized_request_token
        assert self._isJsonizable()
            
    def getNonAuthorizedRequestToken(self):
        token = self._getToken()
        if token:
            assert isinstance(token, OAuthHmacToken)
            if token.auth_state == REQUEST_TOKEN:
                return token

    def setAuthorizedRequestToken(self, authorized_request_token):
        assert isinstance(authorized_request_token, OAuthHmacToken)
        assert authorized_request_token.auth_state == AUTHORIZED_REQUEST_TOKEN
        assert isinstance(self._getToken(), OAuthHmacToken)
        assert self._getToken().auth_state == REQUEST_TOKEN
        self._setToken(authorized_request_token)
        self["authorizedRequestToken"] = authorized_request_token
        assert self._isJsonizable()
            
    def getAuthorizedRequestToken(self):
        token = self._getToken()
        if token:
            assert isinstance(token, OAuthHmacToken)
            if token.auth_state == AUTHORIZED_REQUEST_TOKEN:
                return token
            
    def setAuthorizationUrl(self, authorization_url):
        debug("type of authorization_url is %s" % type(authorization_url))
        assert isinstance(authorization_url, unicode)
        self["authorizationUrl"] = authorization_url
    
    def setAccessToken(self, access_token):
        assert self._isJsonizable()
        assert isinstance(access_token, OAuthHmacToken)
        assert access_token.auth_state == ACCESS_TOKEN
        debug("access token=%s, secret=%s" % (access_token.token, access_token.token_secret))
        self["accessToken"] = access_token
        assert self._isJsonizable()
    
    def getAccessToken(self):
        access_token = self.get("accessToken")
        if access_token:
            assert isinstance(access_token, OAuthHmacToken)
            assert access_token.auth_state == ACCESS_TOKEN
            return access_token
    
    def revoke(self):
        self._delToken()
        
    def _isJsonizable(self):
        try:
            x = dumps(self)
            return True if len(x) else False
        except:
            return None
