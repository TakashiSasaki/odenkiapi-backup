from google.appengine.ext.db import Model, Query
from google.appengine.api.users import User as GoogleUser
from google.appengine.ext.db import StringProperty, URLProperty, IntegerProperty
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication, RequestHandler
from google.appengine.api import oauth
from google.appengine.api import users
from google.appengine.ext.webapp import  template
from Counter import Counter


import logging

class OdenkiUser(Model):
    odenkiId = IntegerProperty()
    odenkiIdMergedTo = IntegerProperty()
    odenkiNickname = StringProperty()
    googleEmail = StringProperty()
    googleNickname = StringProperty()
    googleId = StringProperty()
    docsRequestToken = StringProperty()
    twitterId = StringProperty()
    twitterScreen_name = StringProperty()
    twitterPlaceName = StringProperty()
    twitterPlaceType = StringProperty()
    twitterProfileImage = URLProperty()
    twitterOauthToken = StringProperty()
    twitterOauthTokenSecret = StringProperty()

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
        return result.next()
    except:
        return None
   
class _RequestHandler(RequestHandler):
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
            self.redirect(users.create_login_url())
            return
        
        odenki_user = getByGoogleId(google_user.user_id())
        if odenki_user is None:
            odenki_user = OdenkiUser()
            odenki_user.odenkiNickname =~ google_user.nickname()
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
        v["docsRequestToken"] = odenki_user.docsRequestToken
        self.response.out.write(template.render("html/OdenkiUser.html", v))

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/OdenkiUser', _RequestHandler)]
                                   , debug=True)
    run_wsgi_app(application)
