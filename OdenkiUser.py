from google.appengine.ext.db import Model, Query
from google.appengine.api.users import User as GoogleUser
from google.appengine.ext.db import StringProperty, URLProperty
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication, RequestHandler

import logging

class OdenkiUser(Model):
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

class _RequestHandler(RequestHandler):
    def get(self):
        pass

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/OdenkiUser', _RequestHandler)]
                                   , debug=True)
    run_wsgi_app(application)
