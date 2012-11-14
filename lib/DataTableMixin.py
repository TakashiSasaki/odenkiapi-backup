from model.Columns import Columns, Column
class DataTableMixin(object):
    def to_row(self, _columns):
        """returns an dict object which is convenient for Google Visualization API
           See https://developers.google.com/chart/interactive/docs/reference
        """
        assert isinstance(_columns, Columns)
        c_val = []
        for column in _columns:
            assert isinstance(column, Column)
            c_val.append({
                          "v": getattr(self, column.getId())
                          })
        return {"c" : c_val}
