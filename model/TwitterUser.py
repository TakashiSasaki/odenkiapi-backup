from __future__ import unicode_literals, print_function
from model.NdbModel import NdbModel
from google.appengine.ext import ndb
import gaesessions
from lib.json.JsonRpcError import EntityNotFound, EntityExists, OAuthError
from google.appengine.api import urlfetch
import json
from credentials import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET


class TwitterUser(NdbModel):
    twitterId = ndb.IntegerProperty()
    screenName = ndb.StringProperty(indexed=False)
    accessToken = ndb.StringProperty(indexed=False)
    accessTokenSecret = ndb.StringProperty(indexed=False)
    odenkiId = ndb.IntegerProperty()

    lastUpdated = ndb.DateTimeProperty(indexed=False)
    profile_image_url_https = ndb.StringProperty(indexed=False)
    utc_offset = ndb.IntegerProperty(indexed=False)
    statuses_count = ndb.IntegerProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    friends_count = ndb.IntegerProperty(indexed=False) 
    location = ndb.StringProperty(indexed=False) 
    profile_image_url = ndb.StringProperty(indexed=False)
    screen_name = ndb.StringProperty(indexed=False) 
    lang = ndb.StringProperty(indexed=False) 
    favourites_count = ndb.IntegerProperty(indexed=False) 
    name = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
    created_at = ndb.StringProperty(indexed=False)
    time_zone = ndb.StringProperty(indexed=False)

    SESSION_KEY = "kpi4erdetzytUIitt#%gjgdj"

    @classmethod
    def loadFromSession(cls):
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        if session.has_key(cls.SESSION_KEY):
            twitter_user = session[cls.SESSION_KEY]
            assert isinstance(twitter_user, TwitterUser)
            return twitter_user
        raise EntityNotFound(cls, {"in":"the current session."})
    
    def saveToSession(self):
        try:
            twitter_user = self.loadFromSession()
            assert isinstance(twitter_user, TwitterUser)
            if twitter_user.twitterId == self.twitterId:
                raise EntityExists(self.__class__, {"in_session": twitter_user.twitterId, "to_be_saved": self.twitterId})
        except EntityNotFound: pass
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        session[self.SESSION_KEY] = self

    @classmethod
    def getByTwitterId(cls, twitter_id):
        assert isinstance(twitter_id, int)
        key = cls.keyByTwitterId(twitter_id)
        assert isinstance(key, ndb.Key)
        entity = key.get()
        assert isinstance(entity, TwitterUser)
        return entity
    
    def keyByTwitterId(self, twitter_id):
        assert isinstance(twitter_id, int)
        query = self.queryByTwitterId(twitter_id)
        key = query.get(keys_only=True)
        if key is None:
            raise EntityNotFound(self.__class__, {"twitterId":twitter_id})
        return key

    def setAccessToken(self, access_token, access_token_secret, user_id, screen_name):
        assert isinstance(access_token, str)
        assert isinstance(access_token_secret, str)
        assert isinstance(user_id, int)
        assert isinstance(screen_name, str)
        self.accessToken = access_token
        self.accessTokenSecret = access_token_secret
        self.twitterId = user_id
        self.screenName = screen_name

    def verifyCredentials1(self):
        """this only works with Twitter@Anywhere access token"""
        assert isinstance(self.accessToken, str)
        if self.accessToken is None:
            raise OAuthError("accessToken is not set.")
        verification_result = urlfetch.fetch("https://api.twitter.com/1/account/verify_credentials.json?oauth_access_token=" + self.accessToken)
        if verification_result.status_code != 200:
            raise OAuthError("Can't get verify_credentials with %s as an access token." % self.accessToken)
        d = json.loads(verification_result.content)
        try:
            self.twitterId = d["id"]
            self.screenName = d["screen_name"]
        except KeyError:
            raise OAuthError("Twitter API verify_credentials.json did not return id or screen_name")

    def verifyCredentials11(self):
        import oauth2
        token = oauth2.Token(self.accessToken, self.accessTokenSecret)
        assert isinstance(self.screenName, str)
        assert isinstance(self.twitterId, int)
        #token.set_verifier(oauth_verifier)
        consumer = oauth2.Consumer(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        client = oauth2.Client(consumer, token)
        resp, content = client.request("https://api.twitter.com/1.1/account/verify_credentials.json")
        if resp.status != 200:
            raise OAuthError("Can't get verify_credentials (1.1) with %s as an access token." % self.accessToken)

        d = json.loads(content)
        self.created_at = d.get("created_at")
        self.description = d.get("description")
        self.favourites_count = d.get("favourites_count")
        self.friends_count = d.get("friends_count")
        self.lang = d.get("lang")
        self.location = d.get("location")
        self.name = d.get("name")
        self.profile_image_url = d.get("profile_image_url")
        self.profile_image_url_https = d.get("profile_image_url_https")
        self.screen_name = d.get("screen_name")
        self.statuses_count = d.get("statuses_count")
        self.time_zone = d.get("time_zone")
        self.url = d.get("url")
        self.utc_offset = d.get("utc_offset")

    def overrideBy(self, callback_twitter_user):
        assert isinstance(callback_twitter_user, TwitterUser)
        self.setAccessToken(callback_twitter_user.accessToken, callback_twitter_user.accessTokenSecret, callback_twitter_user.twitterId, callback_twitter_user.screenName)
        self.twitterId = callback_twitter_user.twitterId
        self.screenName = callback_twitter_user.screenName
        
        self.created_at = callback_twitter_user.created_at
        self.description = callback_twitter_user.description
        self.favourites_count = callback_twitter_user.favourites_count
        self.friends_count = callback_twitter_user.friends_count
        self.lang = callback_twitter_user.lang
        self.location = callback_twitter_user.location
        self.name = callback_twitter_user.name
        self.profile_image_url = callback_twitter_user.profile_image_url
        self.profile_image_url_https = callback_twitter_user.profile_image_url_https
        self.screen_name = callback_twitter_user.screen_name
        self.statuses_count = callback_twitter_user.statuses_count
        self.time_zone = callback_twitter_user.time_zone
        self.url = callback_twitter_user.url
        self.utc_offset = callback_twitter_user.utc_offset

    @classmethod
    def getByOdenkiId(cls, odenki_id):
        key = cls.keyByOdenkiId(odenki_id)
        twitter_user = key.get()
        assert isinstance(twitter_user, TwitterUser)
        return twitter_user
    
    @classmethod
    def keyByOdenkiId(cls, odenki_id):
        query = cls.queryByOdenkiId(odenki_id)
        key = query.get(keys_only=True)
        if key is None:
            raise EntityNotFound(cls, {"odenki_id": odenki_id})
        return key
    
    @classmethod
    def queryByOdenkiId(cls, odenki_id):
        query = ndb.Query(kind="TwitterUser")
        query = query.filter(cls.odenkiId == odenki_id)
        return query

    @classmethod
    def deleteAll(cls):
        query = ndb.Query(kind="TwitterUser")
        for key in query:
            assert isinstance(key, ndb.Key)
            key.delete()
