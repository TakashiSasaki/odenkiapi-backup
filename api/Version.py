from google.appengine.ext.webapp import RequestHandler
from lib.CachedContent import CachedContent
from datetime import datetime

class Version(RequestHandler):
    
    def get(self):
        parameter = {
                     "timeStamp" : self.getTimeStamp(),
                     "timeStampString" : self.getTimeStampString(),
                     "versionString" : self.getVersionString()
                     }
        cached_content = CachedContent("/api/Version", parameter, None)
        cached_content.dump()
        cached_content.write(self)
    
    def post(self):
        self.get()
        
    def getTimeStamp(self):
        version_id = self.request.environ["CURRENT_VERSION_ID"].split('.')[1]
        timestamp = long(version_id) / pow(2, 28)
        assert isinstance(timestamp, long)
        return timestamp
    
    def getTimeStampString(self):
        timestamp = self.getTimeStamp()
        return datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d %X UTC")

    def getVersionString(self):
        return self.request.environ["CURRENT_VERSION_ID"].split('.')[0]

from lib import runWsgiApp
if __name__ == "__main__":
    runWsgiApp(Version)
