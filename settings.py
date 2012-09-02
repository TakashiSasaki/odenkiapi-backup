from logging import debug, DEBUG, getLogger
getLogger().setLevel(DEBUG)
debug("settings.py")
from google.appengine.api import memcache
CACHE_BACKEND = 'memcached:///'
