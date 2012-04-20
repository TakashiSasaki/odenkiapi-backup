from google.appengine.ext.db import Model, Query
from google.appengine.ext.db import StringProperty, URLProperty, IntegerProperty
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.api import oauth
from google.appengine.api import users
from Counter import Counter
from GoogleDocs import GoogleDocs
from MyRequestHandler import MyRequestHandler

import logging
import google

class OdenkiUser(Model):
    odenkiId = IntegerProperty()
    odenkiIdMergedTo = IntegerProperty()
    odenkiNickname = StringProperty()
    googleEmail = StringProperty()
    googleNickname = StringProperty()
    googleId = StringProperty()
    docsRequestToken = StringProperty()
    docsCollectionId = StringProperty()
    docsSpreadsheetId = StringProperty()
    docsCommandWorksheetId = StringProperty()
    twitterId = StringProperty()
    twitterScreen_name = StringProperty()
    twitterPlaceName = StringProperty()
    twitterPlaceType = StringProperty()
    twitterProfileImage = URLProperty()
    twitterOauthToken = StringProperty()
    twitterOauthTokenSecret = StringProperty()
    
class OdenkiUserNotFound(Exception):
    pass

def getByGoogleId(google_id):
    query = OdenkiUser.all()
    assert isinstance(query, Query)
    query.filter("googleId = ", google_id)
    result = query.run()
    try:
        return result.next()
    except:
        return None

def getByOdenkiId(odenki_id):
    query = OdenkiUser.all()
    assert isinstance(query, Query)
    query.filter("odenkiId = ", odenki_id)
    result = query.run()
    try:
        odenki_user = result.next()
        assert isinstance(odenki_user, OdenkiUser)
        return odenki_user
    except:
        raise OdenkiUserNotFound()

def getCurrentUser():
    # Currently user authentication relies on Google Account.
    # We will separate Odenki Account and Google Account later.
    google_user = users.get_current_user()
    if google_user is None: 
        raise OdenkiUserNotFound()
    return getByGoogleId(google_user.user_id())

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
            v["googleId"]= "You are not logged in."
            v["googleNickname"]= "You are not logged in."
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
        v["googleEmail"]  = odenki_user.googleEmail
        v["googleId"] = odenki_user.googleId
        v["googleNickname"] = odenki_user.googleNickname
        try: 
            google_docs = GoogleDocs()
            v["docsAccessToken"] = google_docs.loadAccessToken().token
        except:
            pass
        self.writeWithTemplate(v, "OdenkiUser")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/OdenkiUser', _RequestHandler)]
                                   , debug=True)
    run_wsgi_app(application)
