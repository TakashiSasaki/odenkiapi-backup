from __future__ import unicode_literals, print_function
from google.appengine.ext.ndb import Model as _Model
from logging import debug
from model.Columns import Columns

class NdbModel(_Model, Columns):
    
    #_fieldnames = []
    #_columnDescriptions = ColumnDescriptions()
    _columns = None
    
    @classmethod
    def getColumns(cls):
        return cls._columns
    
    def to_list(self):
        """called by JsonRpcDispatcher to create TSV or CSV record.
        This is named after to_dict() which is defined in ndb.Model.
        """
        l = []
        for fieldname in self.getColumnIds():
            l.append(getattr(self, fieldname))
        return l
    
    def to_row(self):
        """returns an dict object which is convenient for Google Visualization API
           See https://developers.google.com/chart/interactive/docs/reference
        """
        c_val = []
        for column_id in self.getColumnIds():
            c_val.append({
                          "v": getattr(self, column_id)
                          })
        return {"c" : c_val}
