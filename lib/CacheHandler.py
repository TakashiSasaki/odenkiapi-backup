from google.appengine.ext.webapp import RequestHandler
import lib
import datetime
from lib.CachedContent import CachedContent

class CacheHandler(RequestHandler):
    __slot__ = ["cachedContent", "httpStatus", "ifModifiedSince"]
    
    def _getIfModifiedSince(self):
        assert not hasattr(self, "ifModifiedSince")
        self.ifModifiedSince = lib.getIfModifiedSince(self.request)
        pass
    
    def get(self):
        self._getIfModifiedSince()
        pass
        
    def setHttpStatus(self, http_status):
        assert not hasattr(self, "httpStatus")
        assert isinstance(http_status, int)
        self.httpStatus = http_status
        self.response.set_status(http_status)

    def writeCachedContent(self, cached_content):
        assert isinstance(cached_content, CachedContent)
        assert not hasattr(self, "ifModifiedSince")
        if cached_content.getLastModified() > self.ifModifiedSince:
            content = cached_content.getContent()
            self.response.out.write(content)
            return

        self.setHttpStatus(304)
        self.response.headers['Content-Type'] = cached_content.getContentType()
        public_string = 'public' if cached_content.isPublic() else 'private'
        max_age = cached_content.getMaxAge()
        if max_age:
            self.response.headers['Cache-Control'] = '%s,max-age=%s' % (public_string, max_age)
        else:
            self.response.headers['Cache-Control'] = '%s' % (public_string)
            assert isinstance(self.lastModified, datetime.datetime)
            self.response.headers['Last-Modified'] = lib.toRfcFormat(self.lastModified)
            self.response.headers['Expires'] = lib.toRfcFormat(self.lastModified + datetime.timedelta(seconds=max_age))
            self.response.out.write(None)

        self.response.headers['Content-Type'] = cached_content.getContentType()
        #self.response.headers['Cache-Control'] = 'private'
        #assert isinstance(self.lastModified, datetime.datetime)
        #response.headers['Last-Modified'] = lib.toRfcFormat(self.lastModified)
        #response.headers['Expires'] = toRfcFormat(self.lastModified + datetime.timedelta(seconds = max_age))
        self.response.out.write(self.content)
        return
