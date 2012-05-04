from google.appengine.ext.db import Model, IntegerProperty, StringProperty
from gdata.gauth import OAuthHmacToken
from credentials import GOOGLE_OAUTH_CONSUMER_KEY, GOOGLE_OAUTH_CONSUMER_SECRET
from gdata.gauth import ACCESS_TOKEN
from gdata.docs.client import DocsClient
from gdata.spreadsheets.client import SpreadsheetsClient
#from OdenkiSession import OdenkiSession
#from google.appengine.api.users import User
#from Counter import getNewOdenkiId
from logging import debug, getLogger, DEBUG
from OdenkiUser import getOdenkiUser, OdenkiUser, createOdenkiUser
getLogger().setLevel(DEBUG)

def getGoogleUser(google_id):
    query = GoogleUser.all()
    query.filter("googleId = ", google_id)
    result = query.run()
    try:
        return result.next()
    except:
        return None

def createGoogleUser(user_id, email, nickname):
    google_user = GoogleUser(googleId = user_id, nickname=nickname, email=email)
    #google_user.email = email
    #google_user.nickname = nickname
    #google_user.userId = user_id
    google_user.put()
    return google_user

class GoogleUser(Model):
    odenkiId = IntegerProperty()
    email = StringProperty(required = True)
    nickname = StringProperty( required = True)
    googleId = StringProperty( required = True)
    accessToken = StringProperty()
    accessTokenSecret = StringProperty()
    collectionId = StringProperty()
    
    def getGoogleId(self):
        return self.googleId
        
    def getOdenkiUser(self):
        if self.odenkiId is None:
            return None
        debug(type(self.odenkiId))
        return getOdenkiUser(self.odenkiId)
    
    def createOdenkiUser(self):
        assert self.odenkiId is None
        odenki_user = createOdenkiUser()
        self.odenkiId = odenki_user.getOdenkiId()
        self.put()
    
    def setOdenkiUser(self, odenki_user):
        assert isinstance(odenki_user, OdenkiUser)
        assert self.getOdenkiUser() is None
        self.odenkiId = odenki_user.getOdenkiId()
        self.put()
    
    def setCanonicalOdenkiId(self, canonical_odenki_id):
        assert isinstance(canonical_odenki_id, int)
        odenki_user = self.getOdenkiUser()
        assert isinstance(odenki_user, OdenkiUser)
        odenki_user.setCanonicalOdenkiId(canonical_odenki_id)
    
    def getCanonicalOdenkiId(self):
        return self.getOdenkiUser().getCanonicalOdenkiId()
     
    def setCollectionId(self, collection_id):
        self.collectionId = collection_id
        self.put()

    def getAccessToken(self ):
        if self.accessToken is None or self.accessTokenSecret is None:
            return None
        oauth_hmac_token = OAuthHmacToken(GOOGLE_OAUTH_CONSUMER_KEY, GOOGLE_OAUTH_CONSUMER_SECRET,
                                          self.accessToken, self.accessTokenSecret, ACCESS_TOKEN)
        assert isinstance(oauth_hmac_token, OAuthHmacToken)
        return oauth_hmac_token

    def setAccessToken(self, oauth_hmac_token):
        assert isinstance(oauth_hmac_token, OAuthHmacToken)
        assert isinstance(oauth_hmac_token.token, str)
        assert oauth_hmac_token.auth_state == ACCESS_TOKEN
        self.accessToken = oauth_hmac_token.token
        assert isinstance(oauth_hmac_token.token_secret, str)
        self.accessTokenSecret = oauth_hmac_token.token_secret
        self.put()
        
        
    def deleteAccessToken(self):
        self.accessToken = None
        self.accessTokenSecret = None
        self.put()
        
    def getDocsClient(self):
        access_token = self.getAccessToken()
        if access_token is None: return None
        assert isinstance(access_token, OAuthHmacToken)
        docs_client = DocsClient()
        docs_client.auth_token = access_token
        return docs_client
    
    def getSpreadsheetsClient(self):
        client = SpreadsheetsClient()
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
