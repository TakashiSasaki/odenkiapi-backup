'''
Created on 2012/01/03

@author: Takashi
'''
import uuid, os, logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from gaesessions import get_current_session
from models import SessionKind
from urllib import urlencode
import logging
import login.credentials
from google.appengine.ext.webapp import template
from models.ObombUserKind import ObombUserKind
from models.TwitterUserKind import TwitterUserKind
from google.appengine.api import urlfetch
from django.utils import simplejson as json

class LoginTwitterRequestHandler(webapp.RequestHandler):
    def get(self):
        current_session = get_current_session()
        if current_session.get(SessionKind.SESSION_ID_KEY) is None:
            current_session[SessionKind.SESSION_ID_KEY] = uuid.uuid1().get_hex()
        session_id = current_session.get(SessionKind.SESSION_ID_KEY)
        
        session_kind_gql = SessionKind.SessionKind.gql("WHERE sessionId = :1", [session_id])
        session_entity = session_kind_gql.get()
        if session_entity is None:
            session_entity = SessionKind.SessionKind()
            session_entity.sessionId = session_id
            session_entity.put()
        assert session_entity is not None

        obomb_user_entity = session_entity.obombUserEntity
        if obomb_user_entity is None:
            obomb_user_entity = ObombUserKind()
        
        twitter_user_entity = obomb_user_entity.twitterUserEntity
        if twitter_user_entity is None:
            twitter_user_entity = TwitterUserKind()
        else:
            template_values = {
                    'session_id' : current_session.get(SessionKind.SESSION_ID_KEY),
                    'access_token' : twitter_user_entity.accessToken,
                    'screen_name' : twitter_user_entity.screenName,
                    'integer_id' : twitter_user_entity.integerId,
                    'verification_error': None
                    }
            path = os.path.join(os.path.dirname(__file__), 'twitter.djhtml')
            self.response.out.write(template.render(path, template_values))
            return
            
        if current_session.get("twitter_authorizing") is True:
            access_token = self.request.get("oauth_access_token")
            current_session["twitter_authorizing"] = False
            verification_result = urlfetch.fetch("https://api.twitter.com/1/account/verify_credentials.json?oauth_access_token=" + access_token)
            if verification_result.status_code != 200:
                template_values = {
                    'session_id' : current_session.get(SessionKind.SESSION_ID_KEY),
                    'access_token' : access_token,
                    'screen_name' : None,
                    'integer_id' : None,
                    'verification_error': True
                    }
                path = os.path.join(os.path.dirname(__file__), 'twitter.djhtml')
                self.response.out.write(template.render(path, template_values))
                return
            verify_credentials = json.loads(verification_result.content)
            logging.debug(verify_credentials)
            integer_id = verify_credentials["id"]
            screen_name = verify_credentials["screen_name"]
            if integer_id is None or screen_name is None:
                template_values = {
                    'session_id' : current_session.get(SessionKind.SESSION_ID_KEY),
                    'access_token' : access_token,
                    'screen_name' : None,
                    'integer_id' : None,
                    'verification_error': True
                    }
                path = os.path.join(os.path.dirname(__file__), 'twitter.djhtml')
                self.response.out.write(template.render(path, template_values))
                return
            twitter_user_entity.integerId = integer_id
            twitter_user_entity.screenName = screen_name
            twitter_user_entity.accessToken = access_token
            twitter_user_entity.put()
            obomb_user_entity.twitterUserEntity = twitter_user_entity
            obomb_user_entity.put()
            template_values = {
                'session_id' : current_session.get(SessionKind.SESSION_ID_KEY),
                'access_token' : access_token,
                'screen_name' : screen_name,
                'integer_id' : integer_id,
                'verification_error' : False 
                }
            path = os.path.join(os.path.dirname(__file__), 'twitter.djhtml')
            self.response.out.write(template.render(path, template_values))
            return

        current_session["twitter_authorizing"] = True
        self.redirect("https://oauth.twitter.com/2/authorize?" + urlencode([("oauth_callback_url", "https://obomb-web.appspot.com/login/twitter"),
                                 ("oauth_mode", "flow_web_client"),
                                 ("oauth_client_identifier", login.credentials.TWITTER_CONSUMER_KEY)]))
        return
    
    def post(self):
        self.get()

if __name__ == "__main__":
    application = webapp.WSGIApplication(
                                     [('/login/twitter', LoginTwitterRequestHandler)],
                                     debug=True)
    run_wsgi_app(application)
