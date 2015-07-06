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


class HexEditor(wx.Panel):

    def __init__(self, *args, **kwags):
        wx.Panel.__init__(self, *args, **kwags)

        hex_grid = wx.grid.Grid(self)
        hex_grid.CreateGrid(10, 16)

        hex_grid.ClipHorzGridLines(False)
        hex_grid.ClipVertGridLines(False)

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


