from google.appengine.ext.db import ReferenceProperty, Model, StringProperty
from MyRequestHandler import MyRequestHandler
from logging import getLogger, DEBUG
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from gaesessions import get_current_session
from OdenkiUser import OdenkiUser

class GoogleUser(Model):
    odenkiUser = ReferenceProperty()
    googleEmail = StringProperty()
    googleNickname = StringProperty()
    googleId = StringProperty()

class _RequestHandler(MyRequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            odenki_user = session.get("odenkiUser")
            assert isinstance(odenki_user, OdenkiUser)
            pass
        pass
    
if __name__ == "__main__":
    getLogger().setLevel(DEBUG)
    application = WSGIApplication([('/GoogleUser', _RequestHandler)]
                                   , debug=True)
    run_wsgi_app(application)
