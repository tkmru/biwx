#!/usr/bin/env python2.7
# coding: UTF-8

__description__ = 'Binary editer'
__author__ = '@tkmru'
__version__ = '0.1'
__date__ = '2015/x/x'
__maximum_python_version__ = (2, 7, 9)
__copyright__ = 'Copyright (c) @tkmru'
__license__ = 'MIT License'

import wx
import wx.grid


class HexGridTable(wx.grid.PyGridTableBase):

    def __init__(self, *args, **kwags):
        wx.grid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', '        Dump       ']
        self.binary_data = [['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']]

    def GetNumberRows(self):
        if len(self.binary_data) > 10:
            return len(self.binary_data)
        else:
            return 10

    def GetNumberCols(self):
        return 17

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # send SetValue
        if row < len(self.binary_data) and col < len(self.binary_data[row]):
            return self.binary_data[row][col]

        else:
            return ''

    def SetValue(self, row, col, value):
        self.data[(row, col)] = value

    def GetColLabelValue(self, col):
        return self.cols_labels[col]

    def GetRowLabelValue(self, row):
        return "0x%X " % (row * 16)


class HexEditor(wx.Panel):

    def __init__(self, *args, **kwags):
        wx.Panel.__init__(self, *args, **kwags)

        hex_grid = wx.grid.Grid(self)
        self.table = HexGridTable()
        hex_grid.SetTable(self.table)

        hex_grid.SetColSize(0, 30)
        hex_grid.SetColSize(1, 30)
        hex_grid.SetColSize(2, 30)
        hex_grid.SetColSize(3, 30)
        hex_grid.SetColSize(4, 30)
        hex_grid.SetColSize(5, 30)
        hex_grid.SetColSize(6, 30)
        hex_grid.SetColSize(7, 30)
        hex_grid.SetColSize(8, 30)
        hex_grid.SetColSize(9, 30)
        hex_grid.SetColSize(10, 30)
        hex_grid.SetColSize(11, 30)
        hex_grid.SetColSize(12, 30)
        hex_grid.SetColSize(13, 30)
        hex_grid.SetColSize(14, 30)
        hex_grid.SetColSize(15, 30)
        hex_grid.SetColSize(16, 200)

        hex_grid.Refresh()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hex_grid, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        file_menu = wx.Menu()

        # On OSX Cocoa both the about and the quit menu belong to the bold 'app menu'.
        file_menu.Append(wx.ID_ABOUT, '&About', 'Information about this program')
        file_menu.Append(wx.ID_PREFERENCES, "&Preferences")
        file_menu.Append(wx.ID_EXIT, '&Exit', 'Terminate the program')

        file_menu.Append(wx.ID_ANY, '&New File')
        file_menu.Append(wx.ID_ANY, '&Open')
        file_menu.Append(wx.ID_ANY, '&Save')

        # Creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.

        self.editor = HexEditor(self)

        self.Fit()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, title='biwx', size=(500, 500))
    frame.Show()
    app.MainLoop()
