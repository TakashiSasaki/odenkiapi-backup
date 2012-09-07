from google.appengine.ext.webapp import RequestHandler
import lib
from google.appengine.api.users import create_login_url, create_logout_url

class UserInfo(RequestHandler):
    
    __slot__ = ["jsonRpc"]
    
    def get(self):
        self.jsonRpc = lib.JsonRpc(self)
        self.setLoginLogoutUrl()

        odenki_session = lib.OdenkiSession()
        self.jsonRpc.setResultValule("sid", odenki_session.getSid())
        odenki_user = odenki_session.getOdenkiUser()
        if odenki_user:
            self.jsonRpc.updateResult(odenki_user.getDictionary())
        google_user = odenki_session.getGoogleUser()
        if google_user:
            self.jsonRpc.updateResult(google_user.getDictionary())
        self.jsonRpc.write()
        return

    def setLoginLogoutUrl(self):
        callback = self.jsonRpc.getParam("callback")
        if callback:
            login_url = create_login_url(callback)
            self.jsonRpc.setResultValule("loginUrl", login_url)
            logout_url = create_logout_url(callback)
            self.jsonRpc.setResultValule("logoutUrl", logout_url)
    
    def post(self):
        self.get()

from lib import runWsgiApp
if __name__ == "__main__":
    runWsgiApp(UserInfo, "/api/SessionInfo")
