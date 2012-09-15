from __future__ import unicode_literals, print_function
from logging import debug, info
from lib.util import Singleton
from _pyio import __metaclass__

class Column(dict):
    """
        type [Required] Data type of the data in the column. Supports the following string values (examples include the v: property, described later):
        'boolean' - JavaScript boolean value ('true' or 'false'). Example value: v:'true'
        'number' - JavaScript number value. Example values: v:7 , v:3.14, v:-55
        'string' - JavaScript string value. Example value: v:'hello'
        'date' - JavaScript Date object (zero-based month), with the time truncated. Example value: v:new Date(2008, 0, 15)
        'datetime' - JavaScript Date object including the time. Example value: v:new Date(2008, 0, 15, 14, 30, 45)
        'timeofday' - Array of three numbers and an optional fourth, representing hour (0 indicates midnight), minute, second, and optional millisecond.    
    """
    def __init__(self, column_id, column_label=None, column_type=None):
        assert isinstance(column_id, unicode)
        assert isinstance(column_label, unicode) or column_label is None
        assert isinstance(column_type, unicode) or column_type is None
        self["id"] = column_id
        self["label"] = column_label if column_label else column_id
        self["type"] = column_type if column_type else "string"

    def getId(self):
        return self["id"]
    
    def getLabel(self):
        return self["label"]
    
    def getType(self):
        return self["type"]

class Columns(list):
    __metaclass__ = Singleton
    
    _TYPE_STRING = "string"
    _TYPE_NUMBER = "number"
    _TYPE_DATE = "date"
    _TYPE_DATETIME = "datetime"
    _TYPE_BOOLEAN = "boolean"
    _TYPE_TIMEOFDAY = "timeofday"
    

    def addColumn(self, column_id, column_label=None, column_type=None):
        self.append(Column(column_id, column_label, column_type))
        
    def addNumber(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, self._TYPE_NUMBER)
    
    def addString(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, self._TYPE_STRING)
    
    def addDate(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, self._TYPE_DATE)

    def addDateTime(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, self._TYPE_DATETIME)

    def addBoolean(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, self._TYPE_BOOLEAN)

    def addTimeOfDay(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, self._TYPE_TIMEOFDAY)

    def getColumnIds(self):
        ids = []
        for x in self:
            debug(x)
            ids.append(x["id"])
        return ids

    def getColumnLabels(self):
        labels = []
        for x in self:
            labels.append(x["label"])
        return labels
    
    def getDataTableCols(self):
        return self
