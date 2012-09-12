from __future__ import unicode_literals, print_function
from logging import debug

class _Column(dict):
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
        self["label"] = column_label if column_label else id
        self["type"] = column_type if column_type else "string"
    

class Columns(object):
    
    _TYPE_STRING = "string"
    _TYPE_NUMBER = "number"
    _TYPE_DATE = "date"
    _TYPE_DATETIME = "datetime"
    _TYPE_BOOLEAN = "boolean"
    _TYPE_TIMEOFDAY = "timeofday"
    _columns = []

    @classmethod
    def addColumn(cls, column_id, column_label=None, column_type=None):
        cls._columns.append(_Column(column_id, column_label, column_type))
        
    @classmethod
    def addNumber(cls, column_id, column_label=None):
        cls.addColumn(column_id, column_label, cls._TYPE_NUMBER)
    
    @classmethod
    def addString(cls, column_id, column_label=None):
        cls.addColumn(column_id, column_label, cls._TYPE_STRING)
    
    @classmethod
    def addDate(cls, column_id, column_label=None):
        cls.addColumn(column_id, column_label, cls._TYPE_DATE)

    @classmethod
    def addDateTime(cls, column_id, column_label=None):
        cls.addColumn(column_id, column_label, cls._TYPE_DATETIME)

    @classmethod
    def addBoolean(cls, column_id, column_label=None):
        cls.addColumn(column_id, column_label, cls._TYPE_BOOLEAN)

    @classmethod
    def addTimeOfDay(cls, column_id, column_label=None):
        cls.addColumn(column_id, column_label, cls._TYPE_TIMEOFDAY)

    @classmethod
    def getColumnIds(cls):
        assert isinstance(cls._columns, list)
        ids = []
        for x in cls._columns:
            debug(x)
            ids.append(x["id"])
        return ids

    @classmethod
    def getColumnLabels(cls):
        labels = []
        for x in cls._columns:
            labels.append(x["label"])
        return labels
