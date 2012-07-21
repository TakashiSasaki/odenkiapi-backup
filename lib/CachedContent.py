import unittest
from google.appengine.api import memcache
#from google.appengine.ext import db
from google.appengine.ext import testbed

from hashlib import md5
import simplejson
import marshal
import datetime
from lib.DateTimeUtil import getNow
from lib.OdenkiSession import OdenkiSession
 

class CachedContent(object):
    __slots__ = ["path", "user", "parameter", "template", "contentType", "lastModified", "public" , "content"]
    
    def __init__(self, path, user, parameter, template=None, content_type=None):
        assert isinstance(path, str)
        self.path = path
        assert isinstance(user, str) or isinstance(user, int) or isinstance(user, long)
        self.user = user
        assert parameter is None or isinstance(parameter, list) or isinstance(parameter, dict)
        self.parameter = parameter
        if template:
            self.template = template
        #self.content = None
        #self.lastModified = None
        # TODO: user should be filled in this constructor
        #self.user = None
        self._save()

    def __str__(self):
        assert isinstance(self.content, str)
        return self.content
    
    def _getKeyHash(self):
        assert isinstance(self.path, str)
        #assert self.user is None or isinstance(self.user, str)
        assert self.parameter is None or isinstance(self.parameter, dict) or isinstance(self.parameter, list)
        assert self.contentType is None or isinstance(self.contentType, str)
        key_list = [self.path, self.user, self.parameter, self.contentType]
        key_string = marshal.dumps(key_list)
        digest_string = md5(key_string).hexdigest()
        return digest_string
    
    def _save(self):
        assert not hasattr(self, "content")
        if hasattr(self, "template"):
            if not hasattr(self, "contentType"):
                self.contentType = "text/html; charset=utf-8"
            self._load()
            if not hasattr(self, "content"):
                from google.appengine.ext.webapp import template
                self.content = template.render(self.template, self.parameter)
        else:
            if not hasattr(self, "contentType"):
                self.contentType = "application/json"
            self._load()
            if not hasattr(self, "content"):                
                self.content = simplejson.dumps(self.parameter)

        if not hasattr(self, "lastModified"):
            self.lastModified = getNow()

        key_hash = self._getKeyHash()
        memcache.add(key_hash, self)
        
    def _load(self):
        "searches for content in memcache and fill empty members."
        assert not hasattr(self, "content")
        loaded_cached_content = memcache.get(self._getKeyHash())
        if loaded_cached_content:
            assert isinstance(loaded_cached_content, self.__class__)
            assert self.path == loaded_cached_content.path
            assert self.parameter == loaded_cached_content.parameter
            from lib import isEqualIfExists
            assert isEqualIfExists(self, loaded_cached_content, "template")
            assert isEqualIfExists(self, loaded_cached_content, "contentType")
            assert not hasattr(self, "lastModified")
            self.lastModified = loaded_cached_content.lastModified
            assert not hasattr(self, "public")
            self.public = loaded_cached_content.public
            assert not hasattr(self, "content")
            self.content = loaded_cached_content.content

    def write(self, request_handler, max_age=600, public=False):
        raise DeprecationWarning
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

class MyTest(unittest.TestCase):
    __stub__ = ["testbed", "user"]
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        
        from lib.OdenkiSession import OdenkiSession
        odenki_session = OdenkiSession()
        self.user = odenki_session.getSid()
    
    def test(self):
        cc1 = CachedContent("/abc", "testuser", [1, "abc"], None)
        print cc1.lastModified
        cc2 = CachedContent("/abc", "testuser", [1, "abc"], None)
        print cc2.lastModified
        
        pass
        
    def tearDown(self):
        self.testbed.deactivate()
    
