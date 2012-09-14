from __future__ import unicode_literals, print_function
from google.appengine.ext.ndb import Model as _Model
from logging import debug
from model.Columns import Column

class NdbModel(_Model):
    
    def to_list(self, _columns):
        """called by JsonRpcDispatcher to create TSV or CSV record.
        This is named after to_dict() which is defined in ndb.Model.
        """
        l = []
        for fieldname in _columns.getColumnIds():
            l.append(getattr(self, fieldname))
        return l
    
    def to_row(self, _columns):
        """returns an dict object which is convenient for Google Visualization API
           See https://developers.google.com/chart/interactive/docs/reference
        """
        c_val = []
        for column in _columns:
            assert isinstance(column, Column)
            c_val.append({
                          "v": getattr(self, column.getId())
                          })
        return {"c" : c_val}
