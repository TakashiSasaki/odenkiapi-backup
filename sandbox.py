class A(object):
    v = 1
    
    @classmethod
    def foo(cls, x):
        cls.v = x
    
class B(A):
    v = 2
    A.foo(3)
    
class C(A):
    v = 4
    A.foo(5)

print B.v
print A.v
