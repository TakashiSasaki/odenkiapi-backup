from google.appengine.ext.db import ReferenceProperty, Model, StringProperty
from MyRequestHandler import MyRequestHandler
from logging import getLogger, DEBUG
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from gaesessions import get_current_session
from OdenkiUser import OdenkiUser
from google.appengine.api import users
from google.appengine.api import oauth

class GoogleUser(Model):
    odenkiUser = ReferenceProperty()
    googleEmail = StringProperty()
    googleNickname = StringProperty()
    googleId = StringProperty()

class _RequestHandler(MyRequestHandler):
    def get(self):
        v = {}
        v["google_logout_url"] = users.create_logout_url("/OdenkiUser")

        try:
            oauth_user = oauth.get_current_user()
            v["oauth_email"] = oauth_user.email()
        except oauth.OAuthRequestError, e:
            v["oauth_email"] = "not authenticated"

        current_user = users.get_current_user()
        if current_user is None:
            v["odenkiId"] = "You are not logged in."
            v["odenkiNickname"] = "You are not logged in."
            v["googleEmail"] = "You are not logged in."
            v["googleId"]= "You are not logged in."
            v["googleNickname"]= "You are not logged in."
            self.writeWithTemplate(v, "OdenkiUser")
            return
        
        session = get_current_session()
        if session.is_active():
            session_user = session.get("odenkiUser")
            assert isinstance(session_user, OdenkiUser)
        else:
            session_user = None
        
        google_user = getByGoogleId(google_user.user_id())
        assert isinstance(google_user, GoogleUser)
        
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
            v["docsAccessToken"] = loadAccessToken().token
        except:
            pass
        self.writeWithTemplate(v, "OdenkiUser")
        
        pass
    
if __name__ == "__main__":
    getLogger().setLevel(DEBUG)
    application = WSGIApplication([('/GoogleUser', _RequestHandler)]
                                   , debug=True)
    run_wsgi_app(application)
