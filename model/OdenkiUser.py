from datetime import datetime
from model.Counter import  Counter
from google.appengine.ext import ndb
from model.NdbModel import NdbModel
import gaesessions
from lib.json.JsonRpcError import EntityNotFound, EntityExists

class OdenkiUser(NdbModel):
    odenkiId = ndb.IntegerProperty(required=True)
    odenkiName = ndb.StringProperty(required=True, indexed=False)
    createdDateTime = ndb.DateTimeProperty(required=True, indexed=False)
    invalidatedDateTime = ndb.DateTimeProperty(indexed=False)
    
    SESSION_KEY = "rgznkwbIBUTIdrvcy"

    def saveToSession(self):
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        try:
            existing = self.loadFromSession()
            assert isinstance(existing, OdenkiUser)
            if existing.odenkiId != self.odenkiId:
                raise EntityExists(self.__class__, {"existing": existing.odenkiId, "odenkiId": self.odenkiId})
        except EntityNotFound: pass
        session[self.SESSION_KEY] = self
    
    @classmethod
    def loadFromSession(cls):
        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        if not session.has_key(cls.SESSION_KEY):
            raise EntityNotFound(cls, {"in": "session"})
        odenki_user = session[cls.SESSION_KEY]
        assert isinstance(odenki_user, OdenkiUser)
        return odenki_user
    
    @classmethod
    def getNew(cls):
        odenki_user = OdenkiUser()
        odenki_user.odenkiId = Counter.GetNextId("odenkiId")
        odenki_user.odenkiName = "Odenki %s" % odenki_user.odenkiId
        odenki_user.createdDateTime = datetime.now()
        key = odenki_user.put()
        assert isinstance(key, ndb.Key)
        entity = key.get()
        assert isinstance(entity, OdenkiUser)
        return entity

    @classmethod
    def queryByOdenkiId(cls, odenki_id):
        assert isinstance(odenki_id, int)
        query = ndb.Query(kind="OdenkiUser")
        query = query.filter(cls.odenkiId == odenki_id)
        return query
    
    @classmethod
    def keyByOdenkiId(cls, odenki_id):
        assert isinstance(odenki_id, int)
        query = cls.queryByOdenkiId(odenki_id)
        key = query.get(keys_only=True)
        if key is None:
            raise EntityNotFound(cls, {"odenkiId": odenki_id})
        assert(key, ndb.Key)
        return key
    
    @classmethod
    def getByOdenkiId(cls, odenki_id):
        assert isinstance(odenki_id, int)
        key = cls.keyByOdenkiId(odenki_id)
        entity = key.get()
        assert isinstance(entity, OdenkiUser)
        return entity
    
#===============================================================================
# class _RequestHandler(MyRequestHandler):
#    def get(self):
#        v = {}
#        v["google_logout_url"] = users.create_logout_url("/OdenkiUser")
# 
#        try:
#            oauth_user = oauth.get_current_user()
#            v["oauth_email"] = oauth_user.email()
#        except oauth.OAuthRequestError, e:
#            v["oauth_email"] = "not authenticated"
# 
#        google_user = users.get_current_user()
#        if google_user is None:
#            v["odenkiId"] = "You are not logged in."
#            v["odenkiNickname"] = "You are not logged in."
#            v["googleEmail"] = "You are not logged in."
#            v["googleId"] = "You are not logged in."
#            v["googleNickname"] = "You are not logged in."
#            self.writeWithTemplate(v, "OdenkiUser")
#            return
#        
#        odenki_user = getByGoogleId(google_user.user_id())
#        if odenki_user is None:
#            odenki_user = OdenkiUser()
#            odenki_user.odenkiNickname = google_user.nickname()
#            odenki_user.odenkiId = Counter.GetNextId("odenkiId")
#            odenki_user.googleEmail = google_user.email()
#            odenki_user.googleId = google_user.user_id()
#            odenki_user.googleNickname = google_user.nickname()
#            odenki_user.put()
# 
#        if odenki_user.odenkiId is None:
#            odenki_user.odenkiId = Counter.GetNextId("odenkiId")
#            odenki_user.put()
# 
#        if odenki_user.odenkiNickname is None:
#            odenki_user.odenkiNickname = odenki_user.googleNickname
#            odenki_user.put()
# 
#        v["odenkiId"] = odenki_user.odenkiId
#        v["odenkiNickname"] = odenki_user.odenkiNickname
#        v["googleEmail"] = odenki_user.googleEmail
#        v["googleId"] = odenki_user.googleId
#        v["googleNickname"] = odenki_user.googleNickname
#        try: 
#            google_docs = GoogleDocs()
#            debug("docsAccessToken = " + google_docs.loadAccessToken().token)
#            v["docsAccessToken"] = google_docs.loadAccessToken().token
#        except:
#            debug("failed to acquire an instance of GoogleDocs")
#            pass
#        self.writeWithTemplate(v, "OdenkiUser")
# 
# if __name__ == "__main__":
#    application = WSGIApplication([('/OdenkiUser', _RequestHandler)]
#                                   , debug=True)
#    run_wsgi_app(application)
#    
#===============================================================================
