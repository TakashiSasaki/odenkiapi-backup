from __future__ import unicode_literals, print_function
from google.appengine.ext import ndb
from model.NdbModel import NdbModel
from logging import debug, info, error
from google.appengine.api.memcache import Client
from gaesessions import Session

context = ndb.get_context()
assert isinstance(context, ndb.Context)
context.set_datastore_policy(lambda key: key.kind() != "AdminUser")

ADMIN_USERS = []
ADMIN_USERS.append("takashi316@gmail.com")
ADMIN_USERS.append("sasaki@odenki.org")
ADMIN_USERS.append("admin@odenki.org")

class AdminUser(NdbModel):
    adminUserName = ndb.StringProperty()

    @classmethod
    def fetchAdminUsers(cls):
        MEMCACHE_KEY = "qc56fhj0kvc1stztiug"
        client = Client()
        admin_users = client.get(MEMCACHE_KEY)
        if admin_users: return admin_users
        admin_users = []
        for admin_user in ADMIN_USERS:
            debug("appending %s" % admin_user)
            a = AdminUser()
            a.adminUserName = admin_user
            key = a.put()
            #assert key is not None
            debug(key)
            admin_users.append(a)
        #debug(admin_users)
        assert isinstance(admin_users, list)
        client.set(MEMCACHE_KEY, admin_users, 100)
        return admin_users

    @classmethod
    def isAdminUser(cls, email):
        for admin_user in cls.fetchAdminUsers():
            if email == admin_user.adminUserName:
                return True
        return False

class AdminMode(bool):
    
    SESSION_KEY = "bezxcgpopiu45eadgobirvuy2"
    
    def setAdminMode(self, admin_mode):
        assert isinstance(admin_mode, bool)
        from gaesessions import get_current_session
        session = get_current_session()
        assert isinstance(session, Session)
        session.set(self.SESSION_KEY, admin_mode)

    def getAdmin