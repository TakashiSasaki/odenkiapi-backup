from hashlib import md5
from marshal import dumps
from datetime import datetime
from google.appengine.api.memcache import get, add

class CachedContent(object):
    def __init__(self, path, user, parameter, content):
        self.path = path
        self.user = user
        self.parameter = parameter
        self.content = content
        self.lastModified = datetime.now()

    def getKeyHash(self):
        return md5(dumps([self.path, self.user, self.parameter])).hexdigest()
    
    def save(self):
        assert self.content is not None
        add(self.getKeyHash(), self)
        
    def load(self):
        loaded_cached_content = get(self.getKeyHash())
        if loaded_cached_content is None:
            self.content = None
            self.lastModified = None
        else:
            assert isinstance(loaded_cached_content, CachedContent)
            self.content = loaded_cached_content.content
            self.lastModified = loaded_cached_content.lastModified
        
if __name__ == "__main__":
    cache_content = CachedContent("/abc", "testuser", None, "hello")
    cache_content.save()
    cache_content = CachedContent("/abc", "testuser", None)
    cache_content.load()
    print cache_content.content
    print cache_content.lastModified
    
