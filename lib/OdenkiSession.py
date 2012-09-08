import unittest
from google.appengine.ext import testbed
from gaesessions import get_current_session, Session, set_current_session
#from GoogleUser import GoogleUser
#from OdenkiUser import getOdenkiUser, OdenkiUser
from logging import debug
#import gaesessions

class OdenkiSession(dict):
    #__slot__=["session"]
    
    def __init__(self):
        try:
            current_session = get_current_session()
            assert isinstance(current_session, Session)
            self.gaesession(current_session)
            assert isinstance(self.gaesession(), Session)
        except:
            current_session = Session()
            assert isinstance(current_session, Session)
            self.gaesession(current_session)
            assert isinstance(self.gaesession(), Session)
        assert isinstance(current_session, Session)
        assert isinstance(self.gaesession(), Session)
        if not current_session.is_active():
            current_session.start()
        assert current_session.is_active()

    def terminate(self):
        self.gaesession().terminate()
        
    def gaesession(self, v=None):
        k = "gaesession"
        if v is None:
            debug("gaesession = %s " % self.get(k)) 
            return self.get(k)
        assert isinstance(v, Session)
        self[k] = v
        assert isinstance(self.get(k), Session)
        
    def passwordAuthState(self, v):
        k = "passwordAuthState"
        if v is None: return self.get(v)
        self[k] = v
    
    def googleAuthState(self, v):
        k = "googleAuthState"
        if v is None: return self.get(k)
        self[k] = v
        
    def googleTwitterState(self, v):
        k = "twitterAuthState"
        if v is None: return self.get(k)
        self[k] = v

    #def getSid(self):
    #    assert isinstance(self.session.sid, str) 
    #   return self.session.sid

    #def revoke(self):
    #   self.deleteGoogleUser()
    #   self.deleteOdenkiUser()

    #def setGoogleUser(self, google_user):
    #    assert isinstance(google_user, GoogleUser)
    #    self.session["googleUser"] = google_user
        
    #def getGoogleUser(self):
    #    try:
    #        google_user = self.session["googleUser"]
    #        return google_user
    #    except KeyError:
    #        return None
    
    #def deleteGoogleUser(self):
    #    try:
    #        del self.session["googleUser"]
    #        #self.session["googleUser"] = None
    #    except KeyError:
    #        pass
    
    #def getOdenkiUser(self):
    #    try:
    #        return self.session["odenkiUser"]
    #    except KeyError:
    #        return None
    
    #def deleteOdenkiUser(self):
    #    try:
    #        self.session["odenkiUser"] = None
    #    except KeyError:
    #        pass
        
    #def getCanonicalOdenkiId(self):
    #    odenki_user = self.getOdenkiUser()
    #    assert isinstance(odenki_user, OdenkiUser)
    #    return odenki_user.getOdenkiId()
    
    #def setOdenkiUser(self, odenki_user):
    #    assert isinstance(odenki_user, OdenkiUser)
    #    try:
    #        assert self.session["odenkiUser"] is None
    #    except KeyError:
    #        pass
    #    self.session["odenkiUser"] = odenki_user
