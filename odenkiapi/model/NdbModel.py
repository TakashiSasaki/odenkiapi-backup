from __future__ import unicode_literals, print_function
from google.appengine.ext.ndb import Model as _Model
#from logging import debug
#from model.Columns import Column, Columns
#from model.DataNdb import Data

class NdbModel(_Model):
    def to_list(self):
        raise RuntimeError("NdbModel.to_dict is obsoleted. Use CsvMixin")
        pass

    def to_row(self):
        raise RuntimeError("NdbModel.to_row is obsoleted. Use DataTableMixin")
