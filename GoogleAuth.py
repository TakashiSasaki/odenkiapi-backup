from logging import debug, DEBUG, getLogger
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
from OdenkiSession import OdenkiSession
from gdata.docs.client import DocsClient
#from google.appengine.ext.db import Model, StringProperty, IntegerProperty
from GoogleUser import getGoogleUser, createGoogleUser, GoogleUser
from google.appengine.api.users import create_login_url, create_logout_url, get_current_user

SCOPE_CALENDER = 'https://www.google.com/calendar/feeds/'
SCOPE_DOCS_LIST = 'https://docs.google.com/feeds/'
SCOPE_SPREADSHEET = 'https://spreadsheets.google.com/feeds/'

GOOGLE_OAUTH_SCOPES = [SCOPE_DOCS_LIST, SCOPE_SPREADSHEET]

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

from OdenkiSession import OdenkiSession

class _RequestHandler(RequestHandler):
    
    __slots__ = ['odenkiSession', 'googleUser']
    
    def get(self):
        if not self.request.accept.accept_html():
            self.response.set_status(406)
            self.response.headers["Content-Type"] = "text/plain; charset=ascii"
            self.response.out.write("Your client should accept text/html; charset=utf-8")

        self.odenkiSession = OdenkiSession()

        if self.request.get("revoke"):
            AeDelete(REQUEST_TOKEN_KEY)
            assert AeLoad(REQUEST_TOKEN_KEY) is None
            self.googleUser = self.odenkiSession.getGoogleUser()
            if self.googleUser:
                google_id = self.googleUser.getGoogleId()
                self.googleUser.delete()
                assert getGoogleUser(google_id) is None
            self.odenkiSession.revoke()
            self.redirect(create_logout_url(self.request.path))
            return

        user = get_current_user()
        if user is None:
            self.redirect(create_login_url(self.request.path))
            return
        assert isinstance(user, User)
        
        self.googleUser = getGoogleUser(user.user_id())
        if self.googleUser is None:
            self.googleUser = createGoogleUser(user.user_id(), user.email(), user.nickname())
        
        if self.odenkiSession.getOdenkiUser() is None:
            if self.googleUser.getOdenkiUser() is None:
                self.googleUser.createOdenkiUser()
            assert isinstance(self.googleUser, GoogleUser)
            self.odenkiSession.setGoogleUser(self.googleUser)
        else:
            if self.googleUser.getOdenkiUser() is None:
                self.googleUser.setOdenkiUser(self.odenkiSession.getOdenkiUser())
            else:
                if self.odenkiSession.getCanonicalOdenkiId() < self.googleUser.getCanonicalOdenkiId():
                    self.googleUser.setCanonicalOdenkiId(self.odenkiSession.getCanonicalOdenkiId())
                elif self.odenkiSession.getCacnonicalOdenkiId() > self.googleUser.getCacnonicalOdenkiId():
                    self.odenkiSession.setCanonicalOdenkiId(self.googleUser.getCanonicalOdenkiId())

        assert self.googleUser.getCanonicalOdenkiId() == self.odenkiSession.getCanonicalOdenkiId()

        debug("trying to load access token")
        if self.googleUser.getAccessToken():
            self.response.headers["Content-Type"] = "text/plain; charset=ascii"
            self.response.out.write("You have already obtained access token.")            
            return

        request_token = AeLoad(REQUEST_TOKEN_KEY)
        if request_token is not None:
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
                self.response.set_status(500)
                self.response.headers["Content-Type"] = "text/plain; charset=ascii"
                self.response.out.write("Couldn't exchange request token to access token.\n")
                self.response.out.write(e.message + "\n")
                self.googleUser.deleteAccessToken()
                AeDelete(REQUEST_TOKEN_KEY)
                self.response.out.write("Request token was deleted.")
                return
        
        assert request_token is None
        try:
            debug("Getting new request token")
            docs_client = DocsClient()
            request_token = docs_client.GetOAuthToken(
                GOOGLE_OAUTH_SCOPES,
                'http://%s/GoogleAuth' % self.request.host,
                GOOGLE_OAUTH_CONSUMER_KEY,
                consumer_secret=GOOGLE_OAUTH_CONSUMER_SECRET)
            assert isinstance(request_token, OAuthHmacToken)
            assert request_token.auth_state == REQUEST_TOKEN
            AeSave(request_token, REQUEST_TOKEN_KEY)
            assert isinstance(AeLoad(REQUEST_TOKEN_KEY), OAuthHmacToken)
            debug("authorizing request token " + str(request_token.generate_authorization_url(google_apps_domain=None)))
            self.redirect(request_token.generate_authorization_url().__str__())
            assert isinstance(AeLoad(REQUEST_TOKEN_KEY), OAuthHmacToken)
            # prompting a page for user to authorize request.
            return
        except:
            self.response.set_status(500)
            self.response.headers["Content-Type"] = "text/plain; charset=ascii"
            self.response.out.write("Failed to get request token.")
            return
        
        # this code should not be reached.
        self.response.headers["Content-Type"] = "text/plain; charset=ascii"
        self.response.out.write("unexpected state in GoogleAuth module.")
        
        
if __name__ == "__main__":
    application = WSGIApplication([('/GoogleAuth', _RequestHandler),
                                   ('/GoogleAuth', _RequestHandler),
                                   ('/GoogleAuth', _RequestHandler)], debug=True)
    run_wsgi_app(application)
