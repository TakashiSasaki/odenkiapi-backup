from __future__ import unicode_literals
from model.Columns import Columns, Column
from model.DataNdb import Data

class CsvMixin(object):

    def to_list_old(self, _columns):
        """called by JsonRpcDispatcher to create TSV or CSV record.
        This is named after to_dict() which is defined in ndb.Model.
        """
        l = []
        for fieldname in _columns.getColumnIds():
            l.append(getattr(self, fieldname))
        return l
    
    def to_list(self, _columns):
        """similar to to_list including dataId resolver.
        """
        assert isinstance(_columns, Columns)
        l = []
        for column in _columns:
            assert isinstance(column, Column)
            if column.isDataField():
                data_id = getattr(self, column.getId())
                if data_id is None:
                    l.append(None)
                    continue
                assert isinstance(data_id, int)
                data = Data.getByDataId(data_id)
                assert isinstance(data, Data)
                assert isinstance(data.field, unicode)
                l.append(data.field)
            if column.isDataString():
                data_id = getattr(self, column.getId())
                if data_id is None:
                    l.append(None)
                    continue
                assert isinstance(data_id, int)
                data = Data.getByDataId(data_id)
                assert isinstance(data, Data)
                assert isinstance(data.string, unicode)
                l.append(data.string)
        return l
    