#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import wx.grid
import scroll_binder


GRID_LINE_COLOUR = '#e7daf7'

ROW_SIZE = 20
ROW_LABEL_SIZE = 70
COL_LABEL_SIZE = 27
DUMP_FONT_SIZE = 12
HEX_FONT_SIZE = 13


class DumpGrid(wx.grid.Grid, scroll_binder.ScrollBinder):

    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        scroll_binder.ScrollBinder.__init__(self)
        self.SetGridLineColour(GRID_LINE_COLOUR)
        self.SetColLabelSize(COL_LABEL_SIZE)
        self.HideRowLabels()
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # http://stackoverflow.com/questions/4852972/wxpython-wx.grid-without-vertical-scrollbar
        self.ShowScrollbars(wx.SHOW_SB_DEFAULT, wx.SHOW_SB_NEVER)

        # Disallow rows stretching vertically and set a fixed height.
        self.DisableDragRowSize()
        self.SetRowMinimalAcceptableHeight(ROW_SIZE)
        self.SetDefaultRowSize(ROW_SIZE, True)
        self.SetScrollRate(self.GetScrollLineX(), ROW_SIZE)


class DumpGridTable(wx.grid.PyGridTableBase):

    def __init__(self, resource):
        wx.grid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self.resource = resource

    def GetNumberRows(self):
        return 100

    def GetNumberCols(self):
        return 16

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # get initial value
        address = row * 32 + col*2
        if address+2 <= len(self.resource.binary):
            ascii_number = int(self.resource.binary[address: address+2], 16)

            if 0 <= ascii_number <= 32 or 127 <= ascii_number:
                return '.'

            else:
                return chr(ascii_number)

        else:
            return ''

    def SetValue(self, row, col, value): # change value
        hex_value = '{0:2x}'.format(ord(value[0])) # 1 char only
        self.resource.insert(row, col, hex_value)

    def GetColLabelValue(self, col):
        return self.cols_labels[col]

    def append_rows(self, number):
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
        self.GetView().ProcessTableMessage(msg)


class HexGrid(wx.grid.Grid, scroll_binder.ScrollBinder):

    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        scroll_binder.ScrollBinder.__init__(self)
        self.SetGridLineColour(GRID_LINE_COLOUR)
        self.SetRowLabelSize(ROW_LABEL_SIZE)
        self.SetColLabelSize(COL_LABEL_SIZE)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        # http://stackoverflow.com/questions/4852972/wxpython-wx.grid-without-vertical-scrollbar
        self.ShowScrollbars(wx.SHOW_SB_DEFAULT, wx.SHOW_SB_NEVER)

        # Disallow rows stretching vertically and set a fixed height.
        self.DisableDragRowSize()
        self.SetRowMinimalAcceptableHeight(ROW_SIZE)
        self.SetDefaultRowSize(ROW_SIZE, True)
        self.SetScrollRate(self.GetScrollLineX(), ROW_SIZE)


class HexGridTable(wx.grid.PyGridTableBase):

    def __init__(self, resource):
        wx.grid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self.resource = resource

    def GetNumberRows(self):
        return 100

    def GetNumberCols(self):
        return 16

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # get initial value
        address = row * 32 + col * 2
        if address+2 <= len(self.resource.binary):
            return self.resource.binary[address: address+2]

        else:
            return ''

    def SetValue(self, row, col, hex_value): # change value
        self.resource.insert(row, col, hex_value)

    def GetColLabelValue(self, col):
        return self.cols_labels[col]

    def GetRowLabelValue(self, row):
        return '0x{0:0>6X}'.format(row * 16)

    def append_rows(self, number):
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
        self.GetView().ProcessTableMessage(msg)
