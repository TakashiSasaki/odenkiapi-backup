from hashlib import md5
from simplejson import dumps
import datetime
import lib

from google.appengine.api import memcache
class CachedContent(object):
    
    __slots__ = ["path", "user", "parameter", "template", "contentType", "content", "lastModified"]
    
    def __init__(self, path, parameter, template=None):
        assert isinstance(path, str)
        self.path = path
        assert parameter is None or isinstance(parameter, list) or isinstance(parameter, dict)
        self.parameter = parameter
        assert parameter is None or isinstance(parameter, list) or isinstance(parameter, dict)
        self.template = template
        self.content = None
        self.lastModified = None
        # TODO: user should be filled in this constructor
        self.user = None

    def getKeyHash(self):
        assert isinstance(self.path, str)
        assert self.user is None or isinstance(self.user, str)
        assert self.parameter is None or isinstance(self.parameter, dict) or isinstance(self.parameter, list)
        assert self.contentType is None or isinstance(self.contentType, str)
        key_list = [self.path, self.user, self.parameter, self.contentType]
        key_string = dumps(key_list)
        digest_string = md5(key_string).hexdigest()
        return digest_string
    
    def save(self):
        assert self.content is not None
        key_hash = self.getKeyHash()
        memcache.add(key_hash, self)
        
    def load(self):
        "searches for content in memcache and fill empty members."
        loaded_cached_content = memcache.get(self.getKeyHash())
        if loaded_cached_content:
            assert isinstance(loaded_cached_content, CachedContent)
            if self.content is None:
                self.content = loaded_cached_content.content
            if self.lastModified is None:
                self.lastModified = loaded_cached_content.lastModified
    
    def render(self):
        self.contentType = "text/html; charset=utf-8"
        self.load()
        if self.content is None:
            from google.appengine.ext.webapp import template
            self.content = template.render(self.template, self.parameter)
        if self.lastModified is None:
            self.lastModified = lib.getNow()
        self.save()
        
    def dump(self):
        self.contentType = "application/json"
        self.load()
        if self.content is None:
            self.content = dumps(self.parameter)
        if self.lastModified is None:
            self.lastModified = lib.getNow()
        self.save()
        
    def text(self):
        self.contentType = "text/plain; charset=utf-8"
        self.load()
        if self.content is None:
            if self.template is None:
                self.content = dumps(self.parameter)
            else:
                self.content = self.template
        if self.lastModified is None:
            self.lastModified = lib.getNow()
        self.save()

    def write(self, request_handler, max_age=600, public=False):
        from google.appengine.ext.webapp import RequestHandler
        assert isinstance(request_handler, RequestHandler)
        request = request_handler.request
        response = request_handler.response
        lib.debug("Last-Modified : " + str(self.lastModified))
        if request.if_modified_since and response.status == 200:
            lib.debug("If-Modified-Since : " + str(request.headers["If-Modified-Since"]))
            if_modified_since = lib.getIfModifiedSince(request)
            assert isinstance(if_modified_since, datetime.datetime)
            assert isinstance(self.lastModified, datetime.datetime)
            if if_modified_since >= self.lastModified:
                response.set_status(304)
                response.headers['Content-Type'] = self.contentType
                public_string = 'public' if public else 'private'
                if max_age:
                    response.headers['Cache-Control'] = '%s,max-age=%s' % (public_string, max_age)
                else:
                    response.headers['Cache-Control'] = '%s' % (public_string)
                assert isinstance(self.lastModified, datetime.datetime)
                response.headers['Last-Modified'] = lib.toRfcFormat(self.lastModified)
                response.headers['Expires'] = lib.toRfcFormat(self.lastModified + datetime.timedelta(seconds=max_age))
                response.out.write(None)
                return
        #response.set_status(200)
        response.headers['Content-Type'] = self.contentType
        response.headers['Cache-Control'] = 'private'
        assert isinstance(self.lastModified, datetime.datetime)
        response.headers['Last-Modified'] = lib.toRfcFormat(self.lastModified)
        #response.headers['Expires'] = toRfcFormat(self.lastModified + datetime.timedelta(seconds = max_age))
        response.out.write(self.content)
        return

if __name__ == "__main__":
    cache_content = CachedContent("/abc", None, "hello")
    cache_content.save()
    cache_content = CachedContent("/abc", None)
    cache_content.load()
    print cache_content.content
    print cache_content.lastModified
