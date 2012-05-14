from logging import debug, DEBUG, getLogger
from lib.JsonRpc import JsonRpc
#from OdenkiUser import getOdenkiUser, NoOdenkiUser
getLogger().setLevel(DEBUG)

from google.appengine.api.users import User
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication, RequestHandler
#from google.appengine.api import users
from gdata.gauth import OAuthHmacToken, ACCESS_TOKEN, AUTHORIZED_REQUEST_TOKEN, REQUEST_TOKEN
#from gdata.docs.data import ResourceFeed, Resource
from credentials import GOOGLE_OAUTH_CONSUMER_KEY, GOOGLE_OAUTH_CONSUMER_SECRET
from gdata.gauth import AeSave, AeLoad, AuthorizeRequestToken, AeDelete
#from gdata.client import Unauthorized
from gdata.docs.client import DocsClient
#from google.appengine.ext.db import Model, StringProperty, IntegerProperty
import lib
from google.appengine.api.users import create_login_url, create_logout_url, get_current_user

SCOPE_CALENDER = 'https://www.google.com/calendar/feeds/'
SCOPE_DOCS_LIST = 'https://docs.google.com/feeds/'
SCOPE_SPREADSHEET = 'https://spreadsheets.google.com/feeds/'

GOOGLE_OAUTH_SCOPES = [SCOPE_DOCS_LIST, SCOPE_SPREADSHEET]

from lib.OdenkiSession import OdenkiSession
odenki_session = OdenkiSession()
#debug("odenki session id = " + odenki_session.getSid())
REQUEST_TOKEN_KEY = odenki_session.getSid() + "_RequestToken"
REQUEST_TOKEN_KEY = "abc"
#def saveAccessToken(access_token):
#    debug("Saving access token " + access_token.token)
#    AeSave(access_token, ACCESS_TOKEN_KEY)

#def loadAccessToken(self):
#    debug("Loading access token by keystring " + self.ACCESS_TOKEN_KEY)
#    access_token = AeLoad(self.ACCESS_TOKEN_KEY)
#    if access_token is None:
#        debug("Loading access token failed")
#    else: 
#        debug("Loading access token succeeded")
#    return access_token

#def deleteAccessToken(self):
#    return AeDelete(self.ACCESS_TOKEN_KEY)

#def getDocsClient(self):
#    client = DocsClient(source='odenkiapi')
#    access_token = self.loadAccessToken()
#    if access_token is not None: 
#        client.auth_token = access_token
#    return client

#def getSpreadsheetsClient(self):
#    client = SpreadsheetsClient(source='odenkiapi')
#    access_token = self.loadAccessToken()
#    if access_token is not None: 
#        assert isinstance(access_token, OAuthHmacToken)
#        OAuthHmacToken
#        client.auth_token = access_token
#    return client

#def getResources(self):
#    client = self.getDocsClient()
#    assert isinstance(client, DocsClient)
#    resource_feed = client.get_resources(show_root=True)
#    return resource_feed

from lib.MethodsHandler import MethodsHandler
from lib.JsonRpc import JsonRpc
class _RequestHandler(MethodsHandler):
    
    def revoke(self, rpc):
        assert isinstance(rpc, JsonRpc)
        AeDelete(REQUEST_TOKEN_KEY)
        assert AeLoad(REQUEST_TOKEN_KEY) is None
        self.googleUser = odenki_session.getGoogleUser()
        if self.googleUser:
            rpc.setResultValule("inSession", True)
            google_id = self.googleUser.getGoogleId()
            rpc.setResultValule("googleId", google_id)
            self.googleUser.delete()
            #assert lib.findGoogleUser(google_id) is None
        else:
            rpc.setResultValule("inSession", False)
            rpc.setResultValule("googleId", None)
        odenki_session.deleteGoogleUser()
        rpc.setResultValule("sid", odenki_session.getSid())
        rpc.addLog("revoked google account")
    
    def default(self, rpc):
        if not self.request.accept.accept_html():
            rpc.setHttpStatus(406)
            rpc.setErrorMessage("user agent does not accept text/html response")
            return

        user = get_current_user()
        if user is None:
            rpc.setResultValule("message", "you are not logged in with google account")
            return
        
        assert isinstance(user, User)        
        self.googleUser = lib.getGoogleUser(user.user_id(), user.email(), user.nickname())
        assert isinstance(self.googleUser, lib.GoogleUser)
        odenki_session.setGoogleUser(self.googleUser)

        if self.googleUser.getAccessToken():
            rpc.setResultValule("message", "You have already obtained access token.")
            return

        request_token = AeLoad(REQUEST_TOKEN_KEY)
        if request_token is not None:
            rpc.addLog("Request token was loaded by AeLoad.")
            rpc.setResultValule("requestToken", request_token.token)
            rpc.setResultValule("requestTokenSecret", request_token.token_secret)
            rpc.setResultValule("requestTokenStatus", request_token.auth_state)
            rpc.setResultValule("sid", odenki_session.getSid())
            assert request_token.auth_state == REQUEST_TOKEN
            debug("Extracting authorized request token from callback URL = " + self.request.url)
            assert isinstance(request_token, OAuthHmacToken)
            authorized_request_token = AuthorizeRequestToken(request_token, self.request.url)
            assert isinstance(authorized_request_token, OAuthHmacToken)
            assert authorized_request_token.auth_state == AUTHORIZED_REQUEST_TOKEN
            AeSave(authorized_request_token, REQUEST_TOKEN_KEY)
            debug("Authorized request token was saved.")
            docs_client = DocsClient()
            try:
                access_token = docs_client.GetAccessToken(authorized_request_token)
                assert isinstance(access_token, OAuthHmacToken)
                assert access_token.auth_state == ACCESS_TOKEN
                debug("access token = " + access_token.token + ", secret = " + access_token.token_secret)
                self.googleUser.setAccessToken(access_token)
                assert isinstance(self.googleUser.getAccessToken(), OAuthHmacToken)
                assert self.googleUser.getAccessToken().auth_state == ACCESS_TOKEN
                self.response.set_status(200)
                self.response.headers["Content-Type"] = "text/plain; charset=ascii"
                self.response.out.write("Access token was saved.\n")
                return
            except Exception, e:
                #self.response.set_status(500)
                #self.response.headers["Content-Type"] = "text/plain; charset=ascii"
                self.googleUser.deleteAccessToken()
                AeDelete(REQUEST_TOKEN_KEY)
                rpc.addLog("Couldn't exchange request token to access token. Request token was deleted.")
                #rpc.setResultValule("message", "Request token was deleted.")
                return
        
        assert request_token is None
        try:
            rpc.addLog("Getting new request token")
            docs_client = DocsClient()
            request_token = docs_client.GetOAuthToken(
                GOOGLE_OAUTH_SCOPES,
                'http://%s/GoogleAuth' % self.request.host,
                GOOGLE_OAUTH_CONSUMER_KEY,
                consumer_secret=GOOGLE_OAUTH_CONSUMER_SECRET)
            assert isinstance(request_token, OAuthHmacToken)
            rpc.addLog("Request token was got")
            rpc.setResultValule("requestToken", request_token.token)
            rpc.setResultValule("requestTokenSecret", request_token.token_secret)
            rpc.setResultValule("requestTokenStatus", request_token.auth_state)
            rpc.setResultValule("sid", odenki_session.getSid())
            AeSave(request_token, REQUEST_TOKEN_KEY)
            assert isinstance(AeLoad(REQUEST_TOKEN_KEY), OAuthHmacToken)
            rpc.addLog("request token was saved by AeSave")
            authorization_url = request_token.generate_authorization_url(google_apps_domain=None)
            rpc.setResultValule("authorizationUrl", str(authorization_url))
            rpc.addLog("redirecting to " + str(authorization_url))
            rpc.redirect(str(authorization_url))
            rpc.addLog("redirection set")
            debug(rpc.requestHandler.response.status)
            # prompting a page for user to authorize request.
            return
        except:
            rpc.addLog("Failed to get request token.")
            return
        
        # this code should not be reached.
        rpc.setResultValule("message", "unexpected state in GoogleAuth module.")
        
        
if __name__ == "__main__":
    from lib import runWsgiApp
    runWsgiApp(_RequestHandler, "/api/GoogleAuth")
