import logging
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
    
    def __init__(self):
        self.odenkiSession = OdenkiSession()
        self.ACCESS_TOKEN_KEY = self.odenkiSession.getSid() + "AccessToken"
        self.REQUEST_TOKEN_KEY = self.odenkiSession.getSid() + "RequestToken"

    def saveRequestToken(self, request_token):
        AeSave(request_token, self.REQUEST_TOKEN_KEY)

    def loadRequestToken(self):
        return AeLoad(self.REQUEST_TOKEN_KEY)

    def deleteRequestToken(self):
        return AeDelete(self.REQUEST_TOKEN_KEY)

    def saveAccessToken(self, access_token):
        logging.debug("Saving access token " + access_token.token)
        AeSave(access_token, self.ACCESS_TOKEN_KEY)

    def loadAccessToken(self):
        logging.debug("Loading access token by keystring " + self.ACCESS_TOKEN_KEY)
        access_token = AeLoad(self.ACCESS_TOKEN_KEY)
        if access_token is None:
            logging.debug("Loading access token failed")
        else: 
            logging.debug("Loading access token succeeded")
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
            client.auth_token = access_token
        return client

    def getResources(self):
        client = self.getDocsClient()
        assert isinstance(client, DocsClient)
        resource_feed = client.get_resources(show_root=True)
        return resource_feed

class _RequestHandler(RequestHandler):
    
    def get(self):
        google_docs = GoogleDocs()

        if self.request.get("revoke"):
            google_docs.deleteAccessToken()
            google_docs.deleteRequestToken()
            self.redirect("/OdenkiUser")
            return
        

        if google_docs.loadRequestToken() is None:
            gdata_client = google_docs.getDocsClient() 
            request_token = gdata_client.GetOAuthToken(
                GOOGLE_OAUTH_SCOPES,
                'http://%s/GoogleDocs' % self.request.host,
                GOOGLE_OAUTH_CONSUMER_KEY,
                consumer_secret=GOOGLE_OAUTH_CONSUMER_SECRET)
            assert isinstance(request_token, OAuthHmacToken)
            google_docs.saveRequestToken(request_token)
            logging.debug("authorizing request token " + str(request_token.generate_authorization_url(google_apps_domain=None)))
            self.redirect(request_token.generate_authorization_url().__str__())
            return
        
        if google_docs.loadAccessToken() is None:
            request_token = google_docs.loadRequestToken()
            logging.debug("Getting access token by request token :" + str(request_token.token))
            assert isinstance(request_token, OAuthHmacToken)
            authorized_request_token = AuthorizeRequestToken(request_token, self.request.url)
            assert isinstance(authorized_request_token, OAuthHmacToken)
            gdata_client = google_docs.getDocsClient()
            try:
                access_token = gdata_client.GetAccessToken(authorized_request_token)
                assert isinstance(access_token, OAuthHmacToken)
                google_docs.saveAccessToken(access_token)
            except Exception, e:
                logging.debug("Can't get access token. " + e.message)
                google_docs.deleteAccessToken()
                google_docs.deleteRequestToken()
                self.redirect("/OdenkiUser")
                return

        assert google_docs.loadAccessToken() is not None
        try:
            resource_feed = google_docs.getResources()
            assert isinstance(resource_feed, ResourceFeed)
        except Unauthorized, e:
            google_docs.deleteRequestToken()
            google_docs.deleteAccessToken()
            self.redirect("/GoogleDocs")
            return
            
        self.redirect("/OdenkiUser")
        return
            
        
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/GoogleDocs', _RequestHandler),
                                   ('/GoogleDocs', _RequestHandler),
                                   ('/GoogleDocs', _RequestHandler)], debug=True)
    run_wsgi_app(application)
