from google.appengine.ext.webapp import RequestHandler
from google.appengine.ext.webapp import  template
from datetime import datetime
from logging import debug
from simplejson import dumps
from google.appengine.api.users import get_current_user, create_login_url, create_logout_url

class MyRequestHandler(RequestHandler):
    def writeWithTemplate(self, values, html_file_name):
        values["version"] =  self.request.environ["CURRENT_VERSION_ID"].split('.')[0]
        version_id = self.request.environ["CURRENT_VERSION_ID"].split('.')[1]
        timestamp = long(version_id) / pow(2,28) 
        values["version_datetime"] = datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d %X UTC")
        if get_current_user() is None:
            values["googleLoginUrl"] = create_login_url()
        else:
            values["googleLogoutUrl"] = create_logout_url("/OdenkiUser")

        self.response.out.write(template.render("html/" + html_file_name + ".html", values))
        
    def writeJson(self, dictionary):
        self.response.content_type = "application/json"
        self.response.out.write(dumps(dictionary))
