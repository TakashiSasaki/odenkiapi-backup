from Singleton import Singleton
isiterable = lambda obj: isinstance(obj, basestring) or hasattr(obj, '__iter__')

#from lib.debug import *
#from logging import debug, DEBUG, getLogger
#getLogger().setLevel(DEBUG)

def getMainModule():
    from sys import modules
    return modules["__main__"]
 
def getMainModuleName():
    from os.path import basename, splitext
    b = basename(getMainModule().__file__)
    (stem, ext) = splitext(b)
    return stem


def isEqualIfExists(o1, o2, a):
    if not hasattr(o1, a) and not hasattr(o2, a): return True
    if not hasattr(o1, a): return False
    if not hasattr(o2, a): return False
    if o1.a != o2.a: return False
    return True

