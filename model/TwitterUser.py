from __future__ import unicode_literals, print_function
from model.NdbModel import NdbModel
from google.appengine.ext import ndb
import gaesessions
from lib.json.JsonRpcError import EntityNotFound, EntityExists

class TwitterUser(NdbModel):
    twitterId = ndb.IntegerProperty()
    screenName = ndb.StringProperty(indexed=False)
    accessToken = ndb.StringProperty(indexed=False)
    odenkiId = ndb.IntegerProperty()

    SESSION_KEY = "kpi4erdetzytUIitt#%gjgdj"

    @classmethod
    def loadFromSession(self):
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        if session.has_key(self.SESSION_KEY):
            twitter_user = session[self.SESSION_KEY]
            assert isinstance(twitter_user, TwitterUser)
            return twitter_user
        raise EntityNotFound(self.__class__, {"in":"the current session."})
    
    def saveToSession(self):
        try:
            twitter_user = self.loadFromSession()
            assert isinstance(twitter_user, TwitterUser)
            if twitter_user.twitterId == self.twitterId:
                raise EntityExists(self.__class__, {"in":"the current session."})
        except EntityNotFound: pass
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        session[self.SESSION_KEY] = self

    def getByTwitterId(self, twitter_id):
        assert isinstance(twitter_id, int)
        key = self.keyByTwitterId(twitter_id)
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
