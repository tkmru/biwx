#!/usr/bin/env python2.7
# coding: UTF-8

__description__ = 'Binary editer'
__author__ = '@tkmru'
__version__ = '0.x'
__date__ = '2015/x/x'
__maximum_python_version__ = (2, 7, 9)
__copyright__ = 'Copyright (c) @tkmru'
__license__ = 'MIT License'

import wx
import wx.grid as wxgrid
import wx.lib.agw.genericmessagedialog as wxgmd
import fy


GRID_LINE_COLOUR = 'blue'


class HexGrid(wxgrid.Grid):

    def __init__(self, parent):
        self.parent = parent
        wxgrid.Grid.__init__(self, self.parent, -1)
        self.SetGridLineColour(GRID_LINE_COLOUR)
        self.SetRowLabelSize(70)
        self.SetColLabelSize(27)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)


class HexGridTable(wxgrid.PyGridTableBase):

    def __init__(self):
        wxgrid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', '        Dump       ']
        self.binary_data = '57656c636f6d6520746f20626977782121'
        self.binary_length = len(self.binary_data)

    def GetNumberRows(self):
        if len(self.binary_data) > 23:
            return len(self.binary_data)
        else:
            return 23

    def GetNumberCols(self):
        return 17

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # get initial value
        addr = row * 32 + col*2

        if addr <= self.binary_length:
            if col < 16:
                return self.binary_data[addr: addr+2]

            else:
                dumped = ''
                for i in range(row*32, (row+1)*32, 2):
                    ascii_number = int(self.binary_data[i: i+2], 16)

                    if 0 <= ascii_number <= 32 or 127 <= ascii_number:
                        dumped += ' . '
                    else:
                        dumped += chr(ascii_number)

                return dumped

        else:
            return ''

    def SetValue(self, row, col, value): # change value
        try:
            self.binary_data[row][col] = value

        except IndexError:
            for i in range(row - len(self.binary_data) + 1):
                self.binary_data.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

            self.binary_data[row][col] = value

    def GetColLabelValue(self, col):
        return self.cols_labels[col]

    def GetRowLabelValue(self, row):
        return '0x{0:X}'.format(row * 16)


class HexEditor(wx.Panel):

    def __init__(self, *args, **kwags):
        wx.Panel.__init__(self, *args, **kwags)

        self.hex_grid = HexGrid(self)
        self.table = HexGridTable()
        self.hex_grid.SetTable(self.table)

        self.hex_grid.SetColSize(0, 30)
        self.hex_grid.SetColSize(1, 30)
        self.hex_grid.SetColSize(2, 30)
        self.hex_grid.SetColSize(3, 30)
        self.hex_grid.SetColSize(4, 30)
        self.hex_grid.SetColSize(5, 30)
        self.hex_grid.SetColSize(6, 30)
        self.hex_grid.SetColSize(7, 30)
        self.hex_grid.SetColSize(8, 30)
        self.hex_grid.SetColSize(9, 30)
        self.hex_grid.SetColSize(10, 30)
        self.hex_grid.SetColSize(11, 30)
        self.hex_grid.SetColSize(12, 30)
        self.hex_grid.SetColSize(13, 30)
        self.hex_grid.SetColSize(14, 30)
        self.hex_grid.SetColSize(15, 30)
        self.hex_grid.SetColSize(16, 200)

        self.hex_grid.Refresh()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.hex_grid, 1, wx.EXPAND)
        self.SetSizerAndFit(sizer)

    def load_file(self, filename):
        try:
            new_binary = fy.get(filename)
            self.table.binary_data = new_binary
            self.table.binary_length = len(new_binary)

            self.hex_grid.ForceRefresh()

        except:
            message_box('Can not open file {0}.'.format(filename), 'Load File Error', wx.OK | wx.ICON_ERROR)


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.CreateStatusBar() # a Statusbar in the bottom of the window

        # setting up the menu.
        file_menu = wx.Menu()

        # on OSX Cocoa both the about and the quit menu belong to the bold 'app menu'.
        file_menu.Append(wx.ID_ABOUT, '&About', 'Information about this program')
        file_menu.Append(wx.ID_PREFERENCES, "&Preferences")
        file_menu.Append(wx.ID_EXIT, '&Exit', 'Terminate the program')

        file_menu.Append(wx.ID_NEW, '&New Window', 'Open new window')
        file_menu.Append(wx.ID_OPEN, '&Open', 'Open file')
        file_menu.Append(wx.ID_SAVE, '&Save')

        # creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)  # adding the MenuBar to the Frame content.
        self.Connect(wx.ID_OPEN, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.open_file_dialog)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor = HexEditor(self)
        sizer.Add(self.editor, 1, wx.EXPAND)

    def _file_dialog(self, *args, **kwargs):
        dialog = wx.FileDialog(self, *args, **kwargs)
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetPath()
            dialog.Destroy()
            return filename

        dialog.Destroy()

    def open_file_dialog(self, event):
        filename = self._file_dialog("Load a file", style=wx.OPEN)
        print filename
        self.editor.load_file(filename)


def message_box(message, title, style=wx.OK | wx.ICON_INFORMATION):
    dialog = wxgmd.GenericMessageDialog(None, message, title, style)
    dialog.ShowModal()
    dialog.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, title='biwx', size=(765, 510))
    frame.Show()
    app.MainLoop()
