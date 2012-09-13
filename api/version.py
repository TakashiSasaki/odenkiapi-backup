#from lib.CachedContent import CachedContent
from datetime import datetime
from lib.gae import *

class _Version(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setResult({
                     "timeStamp" : self._getTimeStamp(),
                     "timeStampString" : self._getTimeStampString(),
                     "versionString" : self._getVersionString()
                     })
        #cached_content = CachedContent(self.request.path, parameter, None)
        #cached_content.dump()
        #cached_content.write(self)
    
    def _getTimeStamp(self):
        version_id = self.request.environ["CURRENT_VERSION_ID"].split('.')[1]
        timestamp = long(version_id) / pow(2, 28)
        assert isinstance(timestamp, long)
        return timestamp
    
    def _getTimeStampString(self):
        timestamp = self._getTimeStamp()
        return datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d %X UTC")

    def _getVersionString(self):
        return self.request.environ["CURRENT_VERSION_ID"].split('.')[0]

if __name__ == "__main__":
    mapping = []
    mapping.append(("/api/version", _Version))
    application = WSGIApplication(mapping)
    run_wsgi_app(application)
