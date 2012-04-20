from logging import debug, DEBUG, getLogger
getLogger().setLevel(DEBUG)

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication, RequestHandler
#from google.appengine.api import users
from gdata.gauth import OAuthHmacToken
from gdata.docs.client import DocsClient
from gdata.spreadsheets.client import SpreadsheetsClient
from gdata.docs.data import ResourceFeed, Resource
from credentials import GOOGLE_OAUTH_CONSUMER_KEY, GOOGLE_OAUTH_CONSUMER_SECRET
from gdata.gauth import AeSave, AeLoad, AuthorizeRequestToken, AeDelete
from gdata.client import Unauthorized
from OdenkiSession import OdenkiSession


SCOPE_CALENDER = 'https://www.google.com/calendar/feeds/'
SCOPE_DOCS_LIST = 'https://docs.google.com/feeds/'
SCOPE_SPREADSHEET = 'https://spreadsheets.google.com/feeds/'

GOOGLE_OAUTH_SCOPES = [SCOPE_DOCS_LIST, SCOPE_SPREADSHEET]

class GoogleDocs():
    __slot__ = ["accessToken", "accessTokenSecret", "odenkiId"]
    
    def __init__(self):
        self.odenkiSession = OdenkiSession()
        debug("an instance of OdenkiSession was acquired")
        self.ACCESS_TOKEN_KEY = self.odenkiSession.getSid() + "AccessToken"
        self.REQUEST_TOKEN_KEY = self.odenkiSession.getSid() + "RequestToken"

    def saveRequestToken(self, request_token):
        AeSave(request_token, self.REQUEST_TOKEN_KEY)

    def loadRequestToken(self):
        return AeLoad(self.REQUEST_TOKEN_KEY)

    def deleteRequestToken(self):
        return AeDelete(self.REQUEST_TOKEN_KEY)

    def saveAccessToken(self, access_token):
        debug("Saving access token " + access_token.token)
        AeSave(access_token, self.ACCESS_TOKEN_KEY)

    def loadAccessToken(self):
        debug("Loading access token by keystring " + self.ACCESS_TOKEN_KEY)
        access_token = AeLoad(self.ACCESS_TOKEN_KEY)
        if access_token is None:
            debug("Loading access token failed")
        else: 
            debug("Loading access token succeeded")
        return access_token

    def deleteAccessToken(self):
        return AeDelete(self.ACCESS_TOKEN_KEY)

    def getDocsClient(self):
        client = DocsClient(source='odenkiapi')
        access_token = self.loadAccessToken()
        if access_token is not None: 
            client.auth_token = access_token
        return client

    def getSpreadsheetsClient(self):
        client = SpreadsheetsClient(source='odenkiapi')
        access_token = self.loadAccessToken()
        if access_token is not None: 
            assert isinstance(access_token, OAuthHmacToken)
            OAuthHmacToken
            client.auth_token = access_token
        return client

    def getResources(self):
        client = self.getDocsClient()
        assert isinstance(client, DocsClient)
        resource_feed = client.get_resources(show_root=True)
        return resource_feed

class _RequestHandler(RequestHandler):
    
    __slots__ = ["googleDocs"]
    
    def get(self):
        try:
            self.googleDocs = GoogleDocs()
        except:
            raise
            debug("Failed to acquire an instance of GoogleDocs")
            self.redirect("/OdenkiUser")
            return

        assert isinstance(self.googleDocs, GoogleDocs)
        debug("GoogleDocs instance acquired")

        if self.request.get("revoke"):
            self.googleDocs.deleteAccessToken()
            self.googleDocs.deleteRequestToken()
            self.redirect("/OdenkiUser")
            return

        if self.googleDocs.loadRequestToken() is None:
            gdata_client = self.googleDocs.getDocsClient() 
            request_token = gdata_client.GetOAuthToken(
                GOOGLE_OAUTH_SCOPES,
                'http://%s/GoogleDocs' % self.request.host,
                GOOGLE_OAUTH_CONSUMER_KEY,
                consumer_secret=GOOGLE_OAUTH_CONSUMER_SECRET)
            assert isinstance(request_token, OAuthHmacToken)
            self.googleDocs.saveRequestToken(request_token)
            debug("authorizing request token " + str(request_token.generate_authorization_url(google_apps_domain=None)))
            self.redirect(request_token.generate_authorization_url().__str__())
            return
        
        if self.googleDocs.loadAccessToken() is None:
            request_token = self.googleDocs.loadRequestToken()
            debug("Getting access token by request token :" + str(request_token.token))
            assert isinstance(request_token, OAuthHmacToken)
            authorized_request_token = AuthorizeRequestToken(request_token, self.request.url)
            assert isinstance(authorized_request_token, OAuthHmacToken)
            gdata_client = self.googleDocs.getDocsClient()
            try:
                access_token = gdata_client.GetAccessToken(authorized_request_token)
                assert isinstance(access_token, OAuthHmacToken)
                self.googleDocs.saveAccessToken(access_token)
            except Exception, e:
                debug("Can't get access token. " + e.message)
                self.googleDocs.deleteAccessToken()
                self.googleDocs.deleteRequestToken()
                self.redirect("/OdenkiUser")
                return

        assert self.googleDocs.loadAccessToken() is not None
        try:
            resource_feed = self.googleDocs.getResources()
            assert isinstance(resource_feed, ResourceFeed)
        except Unauthorized, e:
            self.googleDocs.deleteRequestToken()
            self.googleDocs.deleteAccessToken()
            self.redirect("/GoogleDocs")
            return
            
        self.redirect("/OdenkiUser")
        return
            
        
if __name__ == "__main__":
    application = WSGIApplication([('/GoogleDocs', _RequestHandler),
                                   ('/GoogleDocs', _RequestHandler),
                                   ('/GoogleDocs', _RequestHandler)], debug=True)
    run_wsgi_app(application)
