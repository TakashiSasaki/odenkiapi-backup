from __future__ import unicode_literals, print_function
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from lib.json.JsonRpcError import OAuthError
import json
from logging import debug
from urllib import urlencode
from model.TwitterUser import TwitterUser

class ImplicitFlow(TwitterUser):
    
    """This class supports Twitter@Anywhere API which is similar to OAuth2 implicit flow.
    It is announced that Twitter@Anywhere is to be deprecated.
    """
    
    def __init__(self):
        TwitterUser.__init__(self)

    @classmethod
    def getAuthUrl(cls, consumer_identifier, callback_url):
        """consumer_identifier is identical to consumer key of OAuth 1.0a.
        """
        auth_url = "https://oauth.twitter.com/2/authorize?" 
        auth_url += urlencode([("oauth_callback_url", callback_url),
                     ("oauth_mode", "flow_web_client"),
                     ("oauth_client_identifier", consumer_identifier)])
        return auth_url
    
    def setAccessToken(self, request):
        assert isinstance(request, webapp.Request)
        self.accessToken = request.get("oauth_access_token")
        if self.accessToken is None:
            raise OAuthError({"url":request.url})
        self.verifyCredentials()
