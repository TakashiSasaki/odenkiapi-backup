from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.GmailUser import GmailUser
from google.appengine.api import users
from lib.json.JsonRpcError import EntityNotFound
from model.OdenkiUser import OdenkiUser
from logging import debug

class Gmail(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            gmail_user = GmailUser.loadFromSession()
            assert isinstance(gmail_user, GmailUser)
            jresponse.setResultValue("gmailId", gmail_user.gmailId)
            jresponse.setResultValue("gmail", gmail_user.gmail)
            jresponse.setResultValue("nickname", gmail_user.nickname)
            jresponse.setResultValue("odenkiId", gmail_user.odenkiId)
        except EntityNotFound: pass
        create_url = users.create_login_url("/api/Gmail/RedirectedFromGoogle")
        assert isinstance(create_url, str)
        jresponse.setResultValue("login_url", create_url)

class RedirectedFromGoogle(JsonRpcDispatcher):
    """This is the first handler to catch the result of authentication by Google.
    Binding with OdenkiUser and GmailUser is performed only in this handler.
    """

    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setRedirectTarget("/html/auth/index.html")
        current_user = users.get_current_user()
        if current_user is None:
            return
        debug("type of current_user.user_id() is %s " % type(current_user.user_id()))
        try:
            gmail_user = GmailUser.getByGmailId(current_user.user_id())
            assert isinstance(gmail_user, GmailUser)
        except EntityNotFound:
            gmail_user = GmailUser()

        if gmail_user.odenkiId:
            odenki_user = OdenkiUser.getByOdenkiId(gmail_user.odenkiId)
            assert isinstance(odenki_user, OdenkiUser)
            odenki_user.saveToSession()
        else:
            try:
                odenki_user = OdenkiUser.loadFromSession()
                gmail_user.odenkiId = odenki_user.odenkiId
            except EntityNotFound: pass

        gmail_user.gmail = current_user.email()
        gmail_user.nickname = current_user.nickname()
        gmail_user.saveToSession()
        gmail_user.put()

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/Gmail/RedirectedFromGoogle", RedirectedFromGoogle))
    mapping.append(("/api/Gmail", Gmail))
    from lib.gae import run_wsgi_app
    run_wsgi_app(mapping)

