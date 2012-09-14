class Singleton(type):
    def __init__(self, class_name, base_class, attributes):
        from logging import debug
        debug("Singleton.__init__ was called for class %s with base class %s" % (class_name, base_class))
        type.__init__(self, class_name, base_class, attributes)
        self._instance = None

    def __call__(self, *args):
        from logging import debug
        debug("Singleton.__call__ was called with " % args)
        if self._instance is None :
            self._instance = type.__call__(self, *args)
        return self._instance
