from google.appengine.ext.db import Model, Query
from google.appengine.api.users import User as GoogleUser
from google.appengine.ext.db import StringProperty, URLProperty
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
