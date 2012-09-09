from google.appengine.ext.ndb import Model as _Model

class NdbModel(_Model):
    
    fieldnames = []
    
    def to_list(self):
        """called by JsonRpcDispatcher to create TSV or CSV record.
        This is named after to_dict() which is defined in ndb.Model.
        """
        l = []
        for fieldname in self.__class__.fieldnames:
            l.append(getattr(self, fieldname))
        return l
