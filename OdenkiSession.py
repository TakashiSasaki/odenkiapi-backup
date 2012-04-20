from gaesessions import get_current_session, Session, set_current_session
from logging import getLogger, debug, DEBUG
getLogger().setLevel(DEBUG)

class OdenkiSession(object):
    __slot__=["session"]
    def __init__(self):
        try:
            self.session = get_current_session()
            debug("session was found ")
        except:
            debug("session not found")
            self.session = Session()
            self.session.start()
        if self.session.is_active():
            debug("session is active")
            assert isinstance(self.session.sid, str)
        else:
            debug("session is not active")
            self.session.start()
            assert isinstance(self.session.sid, str) 


    def getSid(self):
        debug(type(self.session.sid))
        assert isinstance(self.session.sid, str) 
        return self.session.sid
