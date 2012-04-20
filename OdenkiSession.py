from gaesessions import get_current_session

class OdenkiSession(object):
    def __init__(self):
        session = get_current_session() 
        if session.is_active():
            assert isinstance(session.sid, str) 
        else:
            session.regenerate_id()

    def getSid(self):
        session = get_current_session()
        assert isinstance(session.sid, str) 
        return session.sid
