from google.appengine.ext.webapp import RequestHandler
from google.appengine.api.users import get_current_user, create_login_url, create_logout_url
from lib.util import getMainModuleName
from lib.debug import *
from lib.gae import JsonRpc
from logging import debug

class BasicPage(RequestHandler):
    
    script = ""
    html = ""
    
    def hasNoParam(self):
        return True if self.request.params.items().__len__() == 0 else False
        
        
    def write(self, html_file=None, script_file=None, title=None):
        if get_current_user() is None:
            self.redirect(create_login_url(self.request.url))
            return
        #else:
        #    self.redirect(create_logout_url(self.request.url))
        #    return
        
        from lib.CachedContent import CachedContent
        parameter = {
                     "script": self.script,
                     "html" : self.html,
                     "title" : title if title else getMainModuleName()
                     }
        if html_file: parameter["htmlFile"] = html_file
        if script_file: parameter["scriptFile"] = script_file

        cached_content = CachedContent(self.request.url, parameter, "html/BasicPage.html")
        cached_content.render()
        cached_content.write(self)
        return

    def doesAcceptJson(self):
        matched = self.request.accept.best_match(["application/json", "application/json-rpc"])
        return True if matched else False
        
    def doesAcceptText(self):
        matched = self.request.accept.best_match(["text/*"])
        return True if matched else False
    
    def get(self):
        debug("MyRequestHandler get")
        if self.request.params.items().__len__() == 0:
            self.write(self.script, self.html)
            return

        json_rpc = JsonRpc(self)
        json_rpc.write()
        return
    
    def post(self):
        json_rpc = JsonRpc(self)
        json_rpc.write()
        return

