from __future__ import unicode_literals, print_function
from google.appengine.ext import db

class Counter(db.Model):
    count = db.IntegerProperty()
    
    @classmethod
    def GetNextId(cls, name):
        def txn():
            obj = cls.get_by_key_name(name)
            if obj is None:
                obj = cls(key_name=name, count=0)
            obj.count += 1
            obj.put()
            return obj.count
        return db.run_in_transaction(txn)
