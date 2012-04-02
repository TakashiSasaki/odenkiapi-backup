import logging
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication, RequestHandler
from google.appengine.ext.webapp import  template
from google.appengine.api import oauth
from google.appengine.api import users
import gdata.gauth
import gdata.docs.client
from credentials import GOOGLE_OAUTH_CONSUMER_KEY, GOOGLE_OAUTH_CONSUMER_SECRET
from OdenkiUser import getByGoogleId, OdenkiUser

GOOGLE_OAUTH_SCOPES = ['https://docs.google.com/feeds/',
                       'https://www.google.com/calendar/feeds/']


class _RequestHandler(RequestHandler):
    def get(self):
        v = {}
        v["google_login_url"] = users.create_login_url("/login")
        v["google_logout_url"] = users.create_logout_url("/login")
        try:
            oauth_user = oauth.get_current_user()
            v["oauth_email"] = oauth_user.email()
        except oauth.OAuthRequestError, e:
            v["oauth_email"] = "not authenticated"
        google_user = users.get_current_user()
        if google_user is not None:
            v["google_user_email"] = google_user.email()
        else:
            v["google_user_email"] = "not authenticated"
            
        if google_user is None:
            self.redirect(users.create_login_url("/login"))
            return
            
        odenki_user = getByGoogleId(google_user.user_id())
        if odenki_user is None:
            u = OdenkiUser()
            u.googleEmail = google_user.email()
            u.googleNickname = google_user.nickname()
            u.googleId = google_user.user_id()
            u.put()
            self.redirect("/login")
            return
        assert isinstance(odenki_user, OdenkiUser)
        
        client = gdata.docs.client.DocsClient(source='odenkiapi')
        docs_request_token = client.GetOAuthToken(
            GOOGLE_OAUTH_SCOPES, 
            'http://%s/login' % self.request.host, 
            GOOGLE_OAUTH_CONSUMER_KEY,
            consumer_secret=GOOGLE_OAUTH_CONSUMER_SECRET)
        assert isinstance(docs_request_token, gdata.gauth.OAuthHmacToken)
        logging.debug(vars(docs_request_token))
        #self.redirect(docs_request_token.generate_authorization_url())
        
        v["docs_request_token"] = docs_request_token.token
        self.response.out.write(template.render("html/login.html", v))
            
        
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/login', _RequestHandler),
                                   ('/google_login', _RequestHandler),
                                   ('/twitter_login',_RequestHandler)], debug=True)
    run_wsgi_app(application)
