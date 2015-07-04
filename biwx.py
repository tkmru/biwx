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

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 500))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        file_menu = wx.Menu()

        file_menu.Append(wx.ID_ABOUT, '&About', 'Information about this program')
        file_menu.Append(wx.ID_PREFERENCES, "&Preferences")
        file_menu.Append(wx.ID_EXIT,'&Exit', 'Terminate the program')

        file_menu.Append(-1, '&New File')
        file_menu.Append(-1, '&Open')
        file_menu.Append(-1, '&Save')

        # Creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.
        self.Show(True)


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, 'biwx')
    app.MainLoop()


