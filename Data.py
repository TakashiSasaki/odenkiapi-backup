from google.appengine.ext import db

class Data(db.Model):
    dataId = db.IntegerProperty()
    name = db.StringProperty
    strings = db.StringListProperty()
    number = db.ListProperty(float)
