from lib.util import Singleton
class A(object):
    __metaclass__ = Singleton

    v = 1
    
    @classmethod
    def foo(cls, x):
        cls.v = x
        
a1 = A()
a2 = A()
print (a1, a2)
    
class B(A):
    v = 2
    A.foo(3)
b1 = B()
b2 = B()
print (b1, b2)
    
class C(A):
    v = 4
    A.foo(5)

print B.v
print A.v
