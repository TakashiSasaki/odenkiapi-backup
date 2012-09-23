from __future__ import unicode_literals, print_function
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from lib.json.JsonRpcError import OAuthError
import json
from logging import debug
from urllib import urlencode

class ImplicitFlow(object):
    
    """This class supports Twitter@Anywhere API which is similar to OAuth2 implicit flow.
    It is announced that Twitter@Anywhere is to be deprecated.
    """
    
    __slots__ = ["accessToken", "authUrl", "verifyCredentials"]
    
    def __init__(self, consumer_identifier, callback_url):
        """consumer_identifier is identical to consumer key of OAuth 1.0a.
        """
        self.authUrl = "https://oauth.twitter.com/2/authorize?" 
        self.authUrl += urlencode([("oauth_callback_url", callback_url),
                     ("oauth_mode", "flow_web_client"),
                     ("oauth_client_identifier", consumer_identifier)])
        self.verifyCredentials = None
    
    def setAccessToken(self, request):
        assert isinstance(request, webapp.Request)
        self.accessToken = request.get("oauth_access_token")
        self._fetchVerifyCredentials()
        
    def fetchVerifyCredentials(self):
        assert self.accessToken
        verification_result = urlfetch.fetch("https://api.twitter.com/1/account/verify_credentials.json?oauth_access_token=" + self.accessToken)
        if verification_result.status_code != 200:
            raise OAuthError("Can't get verify_credentials with %s as an access token." % self.accessToken)
        self.verifyCredentials = json.loads(verification_result.content)
        debug(self.verifyCredentials)
        
    def getId(self):
        if not self.verifyCredentials:
            self.fetchVerifyCredentials()
        assert isinstance(self.verifyCredentials, dict)
        return self.verifyCredentials["id"]
    
    def getScreenName(self):
        if not self.verifyCredentials:
            self.fetchVerifyCredentials()
        assert isinstance(self.verifyCredentials, dict)
        return self.verifyCredentials["screen_name"]
