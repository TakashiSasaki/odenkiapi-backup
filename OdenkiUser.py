from google.appengine.ext.db import Model, Query
from google.appengine.ext.db import StringProperty, URLProperty, IntegerProperty, DateTimeProperty
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.api import oauth
from google.appengine.api import users
from datetime import datetime
from lib.Counter import getNewOdenkiId
#from GoogleDocs import GoogleDocs
from MyRequestHandler import MyRequestHandler

from logging import debug, DEBUG, getLogger
getLogger().setLevel(DEBUG)

class OdenkiUser(Model):
    odenkiId = IntegerProperty(required=True)
    createdDateTime = DateTimeProperty(required=True)
    invalidatedDateTime = DateTimeProperty()
    canonicalOdenkiId = IntegerProperty(required=True)
    
    def getOdenkiId(self):
        return self.odenkiId

    def setOdenkiId(self, odenki_id):
        assert self.odenkiId is None
        assert isinstance(odenki_id, int)
        self.odenkiId = odenki_id
        self.put()
    
    def getCanonicalOdenkiId(self):
        return self.canonicalOdenkiId
    
    def setCanonicalOdenkiId(self, canonical_odenki_id):
        assert isinstance(canonical_odenki_id, int)
        assert self.odenkiId >= canonical_odenki_id
        assert self.canonicalOdenkiId > canonical_odenki_id
        self.canonicalOdenkiId = canonical_odenki_id
        self.put()
    
    def isInvalid(self):
        if self.invalidatedDateTime:
            return True
        else:
            return False
    
    def invalidate(self):
        assert self.invalidatedDateTime is None
        self.invalidatedDateTime = datetime.now()
        assert self.invalidatedDateTime >= self.createdDateTime
        self.put()
    
def getOdenkiUser(odenki_id):
    assert isinstance(odenki_id, long)
    query = OdenkiUser.all()
    assert isinstance(query, Query)
    query.filter("odenkiId = ", odenki_id)
    result = query.run()
    try:
        odenki_user = result.next()
        assert isinstance(odenki_user, OdenkiUser)
        return odenki_user
    except:
        return None

def createOdenkiUser():
    odenki_id = getNewOdenkiId()
    odenki_user = OdenkiUser(odenkiId=odenki_id, canonicalOdenkiId=odenki_id, createdDateTime=datetime.now())
    odenki_user.put()
    return odenki_user

class _RequestHandler(MyRequestHandler):
    def get(self):
        v = {}
        v["google_logout_url"] = users.create_logout_url("/OdenkiUser")

        try:
            oauth_user = oauth.get_current_user()
            v["oauth_email"] = oauth_user.email()
        except oauth.OAuthRequestError, e:
            v["oauth_email"] = "not authenticated"

        google_user = users.get_current_user()
        if google_user is None:
            v["odenkiId"] = "You are not logged in."
            v["odenkiNickname"] = "You are not logged in."
            v["googleEmail"] = "You are not logged in."
            v["googleId"] = "You are not logged in."
            v["googleNickname"] = "You are not logged in."
            self.writeWithTemplate(v, "OdenkiUser")
            return
        
        odenki_user = getByGoogleId(google_user.user_id())
        if odenki_user is None:
            odenki_user = OdenkiUser()
            odenki_user.odenkiNickname = google_user.nickname()
            odenki_user.odenkiId = Counter.GetNextId("odenkiId")
            odenki_user.googleEmail = google_user.email()
            odenki_user.googleId = google_user.user_id()
            odenki_user.googleNickname = google_user.nickname()
            odenki_user.put()

        if odenki_user.odenkiId is None:
            odenki_user.odenkiId = Counter.GetNextId("odenkiId")
            odenki_user.put()

        if odenki_user.odenkiNickname is None:
            odenki_user.odenkiNickname = odenki_user.googleNickname
            odenki_user.put()

        v["odenkiId"] = odenki_user.odenkiId
        v["odenkiNickname"] = odenki_user.odenkiNickname
        v["googleEmail"] = odenki_user.googleEmail
        v["googleId"] = odenki_user.googleId
        v["googleNickname"] = odenki_user.googleNickname
        try: 
            google_docs = GoogleDocs()
            debug("docsAccessToken = " + google_docs.loadAccessToken().token)
            v["docsAccessToken"] = google_docs.loadAccessToken().token
        except:
            debug("failed to acquire an instance of GoogleDocs")
            pass
        self.writeWithTemplate(v, "OdenkiUser")

if __name__ == "__main__":
    application = WSGIApplication([('/OdenkiUser', _RequestHandler)]
                                   , debug=True)
    run_wsgi_app(application)
    
