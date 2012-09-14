CACHE_BACKEND = 'memcached:///'

import logging as _logging
_logging.getLogger().setLevel(_logging.DEBUG)

import sys as _sys
_sys.setrecursionlimit = 5
