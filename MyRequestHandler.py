from google.appengine.ext.webapp import RequestHandler
from google.appengine.ext.webapp import  template
from datetime import datetime
from logging import debug

class MyRequestHandler(RequestHandler):
    def writeWithTemplate(self, values, html_file_name):
        values["version"] =  self.request.environ["CURRENT_VERSION_ID"].split('.')[0]
        version_id = self.request.environ["CURRENT_VERSION_ID"].split('.')[1]
        timestamp = long(version_id) / pow(2,28) 
        values["version_datetime"] = datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d %X UTC")
        self.response.out.write(template.render("html/" + html_file_name + ".html", values))
        
