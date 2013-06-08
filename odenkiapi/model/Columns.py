from __future__ import unicode_literals, print_function
from logging import debug
from lib.util import Singleton

# These column types correspond with google.visualization.DataTable .
# https://developers.google.com/chart/interactive/docs/reference#DataTable

COLUMN_TYPE_STRING = "string"
COLUMN_TYPE_NUMBER = "number"
COLUMN_TYPE_DATE = "date"
COLUMN_TYPE_DATETIME = "datetime"
COLUMN_TYPE_BOOLEAN = "boolean"
COLUMN_TYPE_TIMEOFDAY = "timeofday"

#TODO: does these two column type are really needed?
COLUMN_TYPE_DATA_FIELD = "datafield"
COLUMN_TYPE_DATA_STRING = "datastring"


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

    def isString(self):
        return self.getType() == COLUMN_TYPE_STRING

    def isNumber(self):
        return self.getType() == COLUMN_TYPE_NUMBER

    def isDate(self):
        return self.getType() == COLUMN_TYPE_DATE

    def isDateTime(self):
        return self.getType() == COLUMN_TYPE_DATETIME

    def isBoolean(self):
        return self.getType() == COLUMN_TYPE_BOOLEAN

    def isTimeOfDay(self):
        return self.getType() == COLUMN_TYPE_TIMEOFDAY

    def isDataField(self):
        return self.getType() == COLUMN_TYPE_DATA_FIELD

    def isDataString(self):
        return self.getType() == COLUMN_TYPE_DATA_STRING


class Columns(list):
    __metaclass__ = Singleton
    __slots__ = []

    def addColumn(self, column_id, column_label=None, column_type=None):
        self.append(Column(column_id, column_label, column_type))

    def addNumber(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_NUMBER)

    def addString(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_STRING)

    def addDate(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_DATE)

    def addDateTime(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_DATETIME)

    def addBoolean(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_BOOLEAN)

    def addTimeOfDay(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_TIMEOFDAY)

    def addDataField(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_DATA_FIELD)

    def addDataString(self, column_id, column_label=None):
        self.addColumn(column_id, column_label, COLUMN_TYPE_DATA_STRING)

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

import unittest
class _TestCase(unittest.TestCase):
    def setUp(self):
        self.column1 = Column("name", "Name")
        self.column2 = Column("age", "Age", COLUMN_TYPE_NUMBER)
        self.columns1 = Columns()
        self.columns1.addDate("pn", "Product Name")

    def test(self):
        self.assertEqual(self.column1.getId(), "name")
        self.assertEqual(self.column1.getLabel(), "Name")
        self.assertEqual(self.columns1.getColumnIds(), ["pn"])

if __name__ == "__main__":
    unittest.main()