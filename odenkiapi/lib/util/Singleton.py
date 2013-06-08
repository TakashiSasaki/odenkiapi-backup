class Singleton(type):
    def __init__(self, class_name, base_class, attributes):
        from logging import debug

        debug("Singleton.__init__ was called for class %s with base class %s" % (class_name, base_class))
        type.__init__(self, class_name, base_class, attributes)
        self._instance = None

    def __call__(self, *args):
        from logging import debug

        debug("Singleton.__call__ was called with " % args)
        if self._instance is None:
            self._instance = type.__call__(self, *args)
        return self._instance


import unittest, logging


class _TestSingleton():
    __metaclass__ = Singleton
    pass


class _TestCase(unittest.TestCase):

    def setUp(self):
        logging.debug("setUp")
        pass

    def tearDown(self):
        print("tearDown")
        pass

    def test(self):
        test_singleton_1 = _TestSingleton()
        self.assertFalse(hasattr(test_singleton_1, "x"))
        test_singleton_2 = _TestSingleton()
        test_singleton_1.x = 1
        self.assertTrue(hasattr(test_singleton_1, "x"))
        self.assertEqual(test_singleton_1.x, 1)
        test_singleton_2.x = 2
        self.assertTrue(hasattr(test_singleton_1, "x"))
        self.assertEqual(test_singleton_1.x, 2)


if __name__ == "__main__":
    unittest.main()