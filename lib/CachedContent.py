from hashlib import md5
import dateutil.parser
from simplejson import dumps
import datetime
from logging import DEBUG, debug, getLogger
getLogger().setLevel(DEBUG)

ANCIENT = "Fri, 01 Jan 1990 00:00:00 GMT"

class GMT(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=0)
    def dst(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return "GMT"

def getNow():
    dt = datetime.datetime.now()
    assert isinstance(dt, datetime.datetime)
    dt = dt.replace(tzinfo=GMT())
    s = toRfcFormat(dt)
    dt = toDateTime(s)
    return dt

def getIfModifiedSince(request):
    from google.appengine.ext.webapp import Request
    assert isinstance(request, Request)
    s = request.headers.get("If-Modified-Since", None)
    return toDateTime(s)

def toDateTime(s):
    if s is None:
        dt = dateutil.parser.parse(ANCIENT)
        assert isinstance(dt, datetime.datetime)
        assert dt.tzinfo is not None
        return dt 
    else:
        assert isinstance(s, str)
        dt = dateutil.parser.parse(s)
        assert isinstance(dt, datetime.datetime)
        assert dt.tzinfo is not None
        return dt

def toRfcFormat(dt):
    if dt is None:
        return ANCIENT
    assert isinstance(dt, datetime.datetime)
    assert dt.tzinfo is not None
    return dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

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
        return md5(dumps([self.path, self.user, self.parameter, self.contentType])).hexdigest()
    
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
            self.lastModified = getNow()
        self.save()
        
    def dump(self):
        self.contentType = "application/json"
        self.load()
        if self.content is None:
            self.content = dumps(self.parameter)
        if self.lastModified is None:
            self.lastModified = getNow()
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
            self.lastModified = getNow()
        self.save()

    def write(self, request_handler, max_age = 600, public = False):
        from google.appengine.ext.webapp import RequestHandler
        assert isinstance(request_handler, RequestHandler)
        request = request_handler.request
        response = request_handler.response
        debug("Last-Modified : " + str(self.lastModified))
        if request.if_modified_since:
            debug("If-Modified-Since : " + str(request.headers["If-Modified-Since"]))
            if_modified_since = getIfModifiedSince(request)
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
                response.headers['Last-Modified'] = toRfcFormat(self.lastModified)
                response.headers['Expires'] = toRfcFormat(self.lastModified + datetime.timedelta(seconds = max_age))
                response.out.write(None)
                return
        response.set_status(200)
        response.headers['Content-Type'] = self.contentType
        response.headers['Cache-Control'] = 'private'
        assert isinstance(self.lastModified, datetime.datetime)
        response.headers['Last-Modified'] = toRfcFormat(self.lastModified)
        #response.headers['Expires'] = toRfcFormat(self.lastModified + datetime.timedelta(seconds = max_age))
        response.out.write(self.content)
        return

if __name__ == "__main__":
    now_datetime = getNow()
    now_string = toRfcFormat(now_datetime)
    now_datetime2 = toDateTime(now_string)
    assert now_datetime2 == now_datetime2
    debug("test finished")
    cache_content = CachedContent("/abc", None, "hello")
    cache_content.save()
    cache_content = CachedContent("/abc", None)
    cache_content.load()
    print cache_content.content
    print cache_content.lastModified
