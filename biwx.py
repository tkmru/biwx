#!/usr/bin/env python2.7
# coding:UTF-8

import wx
import wx.grid as wxgrid
import wx.lib.agw.genericmessagedialog as wxgmd
import fy
# from multiprocessing import Process


GRID_LINE_COLOUR = '#e7daf7'
BACKGROUND_COLOUR = 'white'

ROW_SIZE = 20
ROW_LABEL_SIZE = 70
COL_LABEL_SIZE = 27


class ScrollBinder(object):

    '''
    http://wxpython-users.1045709.n5.nabble.com/Scrolling-grids-simultaneously-td2349695.html
    Inherit to be able to bind vscrolling to another widget.
    '''

    def __init__(self):
        '''
        f() -> ScrollBinder
        Initialises the internal data required for vertical scrolling.
        '''
        self._locked = False
        self._bound_widget = None
        self._is_list_control = hasattr(self, 'ScrollList')

        #self.Bind(wx.EVT_SCROLLWIN, self._did_scroll)
        self.Bind(wx.EVT_MOUSEWHEEL, self._mousewheel)
        self.Bind(wx.EVT_SCROLLWIN_LINEUP, self._lineup)
        self.Bind(wx.EVT_SCROLLWIN_LINEDOWN, self._linedown)
        self.Bind(wx.EVT_SCROLLWIN_PAGEUP, self._pageup)
        self.Bind(wx.EVT_SCROLLWIN_PAGEDOWN, self._pagedown)
        self.Bind(wx.EVT_SCROLLWIN_TOP, self._top)
        self.Bind(wx.EVT_SCROLLWIN_BOTTOM, self._bottom)
        self.Bind(wx.EVT_KEY_DOWN, self._key_down)

    def bind_scroll(self, target):
        self._bound_widget = target

    def _key_down(self, event):
        pass

    def _mousewheel(self, event):
        '''Mouse wheel scrolled. Up or down, give or take.'''
        try:
            if event.m_wheelRotation > 0:
                do_scroll = self._lineup
            else:
                do_scroll = self._linedown

            for r in range(event.m_linesPerAction):
                do_scroll()

        except AttributeError:
            pass

    def _pageup(self, event):
        '''Clicked on a scrollbar space, performing a page up.'''
        if event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        pos = self.GetScrollPos(wx.VERTICAL)
        if self._is_list_control:
            amount = self.GetCountPerPage()
        else:
            amount = self.GetScrollPageSize(wx.VERTICAL)

        self._bound_widget.scroll_to(max(0, pos - amount))
        self.scroll_to(max(0, pos - amount))

    def _pagedown(self, event):
        '''Clicked on a scrollbar space, performing a page down.'''
        if event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        pos = self.GetScrollPos(wx.VERTICAL)
        if self._is_list_control:
            amount = self.GetCountPerPage()
        else:
            amount = self.GetScrollPageSize(wx.VERTICAL)

        self._bound_widget.scroll_to(pos + amount)
        self.scroll_to(pos + amount)

    def _top(self, event):
        '''Event handler for going to the top.'''
        if event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        self._bound_widget.scroll_to(0)
        self.scroll_to(0)

    def _bottom(self, event):
        '''Event handler for going to the bottom.'''
        if event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        pos = 10000000
        self._bound_widget.scroll_to(pos)
        self.scroll_to(pos)

    def _lineup(self, event=None): # maybe wrong
        '''Event handler for pressing the up arrow.'''
        if event and event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        pos = self.GetScrollPos(wx.VERTICAL)
        self._bound_widget.scroll_to(pos)
        self.scroll_to(pos)

    def _linedown(self, event=None):
        '''Event handler for pressing the down arrow.'''
        if event and event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        pos = self.GetScrollPos(wx.VERTICAL)
        print pos
        self.scroll_to(pos)
        self._bound_widget.scroll_to(pos)

    def _did_scroll(self, event):
        '''Event handler for manual scrolling.'''
        try:
            if event.GetOrientation() != wx.VERTICAL or self._locked:
                return

        finally:
            event.Skip()

    def scroll_to(self, position):
        '''
        f(int)-> None
        Scrolls to a specific vertical position.
        '''
        self._locked = True

        if self._is_list_control:
            diff = position - self.GetScrollPos(wx.VERTICAL)
            self.ScrollList(-1, diff * ROW_SIZE)

        else:
            # Presume we are a grid.
            self.Scroll(-1, position)

        self._locked = False


class DumpGrid(wxgrid.Grid, ScrollBinder):

    def __init__(self, parent):
        self.parent = parent
        wxgrid.Grid.__init__(self, self.parent, -1)
        ScrollBinder.__init__(self)
        self.SetGridLineColour(GRID_LINE_COLOUR)
        self.SetColLabelSize(COL_LABEL_SIZE)
        self.HideRowLabels()
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Disallow rows stretching vertically and set a fixed height.
        self.DisableDragRowSize()
        self.SetRowMinimalAcceptableHeight(ROW_SIZE)
        self.SetDefaultRowSize(ROW_SIZE, True)
        self.SetScrollRate(self.GetScrollLineX(), ROW_SIZE)


class DumpGridTable(wxgrid.PyGridTableBase):

    def __init__(self):
        wxgrid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self.binary_data = '57656c636f6d6520746f20626977782121'
        self.binary_length = len(self.binary_data)

    def GetNumberRows(self):
        if len(self.binary_data) > 23:
            return len(self.binary_data)
        else:
            return 23

    def GetNumberCols(self):
        return 16

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # get initial value
        address = row * 32 + col*2
        if address+2 <= self.binary_length:
            ascii_number = int(self.binary_data[address: address+2], 16)

            if 0 <= ascii_number <= 32 or 127 <= ascii_number:
                return '.'

            else:
                return chr(ascii_number)

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


class HexGrid(wxgrid.Grid, ScrollBinder):

    def __init__(self, parent):
        self.parent = parent
        wxgrid.Grid.__init__(self, self.parent, -1)
        ScrollBinder.__init__(self)
        self.SetGridLineColour(GRID_LINE_COLOUR)
        self.SetRowLabelSize(ROW_LABEL_SIZE)
        self.SetColLabelSize(COL_LABEL_SIZE)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        # http://stackoverflow.com/questions/4852972/wxpython-wxgrid-without-vertical-scrollbar
        self.ShowScrollbars(wx.SHOW_SB_DEFAULT, wx.SHOW_SB_NEVER)

        # Disallow rows stretching vertically and set a fixed height.
        self.DisableDragRowSize()
        self.SetRowMinimalAcceptableHeight(ROW_SIZE)
        self.SetDefaultRowSize(ROW_SIZE, True)
        self.SetScrollRate(self.GetScrollLineX(), ROW_SIZE)


class HexGridTable(wxgrid.PyGridTableBase):

    def __init__(self):
        wxgrid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self.binary_data = '57656c636f6d6520746f20626977782121'
        self.binary_length = len(self.binary_data)

    def GetNumberRows(self):
        if len(self.binary_data) > 23:
            return len(self.binary_data)
        else:
            return 23

    def GetNumberCols(self):
        return 16

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # get initial value
        address = row * 32 + col*2
        if address+2 <= self.binary_length:
            return self.binary_data[address: address+2]

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


class Editor(wx.Panel):

    def __init__(self, *args, **kwags):
        wx.Panel.__init__(self, *args, **kwags)

        self.hex_grid = HexGrid(self)
        self.hex_table = HexGridTable()
        self.hex_grid.SetTable(self.hex_table)

        self.dump_grid = DumpGrid(self)
        self.dump_table = DumpGridTable()
        self.dump_grid.SetTable(self.dump_table)

        # Bind the scrollbars of the widgets.
        self.hex_grid.bind_scroll(self.dump_grid)
        self.dump_grid.bind_scroll(self.hex_grid)

        for i in range(0, 16):
            self.hex_grid.SetColSize(i, 30)

        for i in range(0, 16):
            self.dump_grid.SetColSize(i, 15)

        self.hex_grid.Refresh()
        self.dump_grid.Refresh()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.hex_grid, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=10)
        sizer.Add(self.dump_grid, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)

    def load_file(self, file_path):
        try:
            new_binary = fy.get(file_path)
            self.hex_table.binary_data = new_binary
            self.hex_table.binary_length = len(new_binary)
            self.hex_grid.ForceRefresh()

            self.dump_table.binary_data = new_binary
            self.dump_table.binary_length = len(new_binary)
            self.dump_grid.ForceRefresh()

        except:
            message_box('Can not open file {0}.'.format(file_path), 'Load File Error', wx.OK | wx.ICON_ERROR)


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.CreateStatusBar() # a Statusbar in the bottom of the window

        # setting up the menu.
        file_menu = wx.Menu()

        # on OSX Cocoa both the about and the quit menu belong to the bold 'app menu'.
        file_menu.Append(wx.ID_ABOUT, '&About', 'Information about this program')
        file_menu.Append(wx.ID_PREFERENCES, '&Preferences')
        file_menu.Append(wx.ID_EXIT, '&Exit', 'Terminate the program')

        file_menu.Append(wx.ID_NEW, '&New Window', 'Open new window')
        file_menu.Append(wx.ID_OPEN, '&Open', 'Open file')
        file_menu.Append(wx.ID_SAVE, '&Save')

        # creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)  # adding the MenuBar to the Frame content.
        self.Connect(wx.ID_OPEN, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.open_file_dialog)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor = Editor(self)
        sizer.Add(self.editor, 1, wx.EXPAND)

        self.SetBackgroundColour(BACKGROUND_COLOUR)

    def _file_dialog(self, *args, **kwargs):
        dialog = wx.FileDialog(self, *args, **kwargs)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            dialog.Destroy()

            return file_path

        dialog.Destroy()

    def open_file_dialog(self, event):
        file_path = self._file_dialog('Load a file', style=wx.OPEN)
        print file_path
        self.editor.load_file(file_path)
        self.SetStatusText('Opened file "{0}".'.format(file_path))


def message_box(message, title, style=wx.OK | wx.ICON_INFORMATION):
    dialog = wxgmd.GenericMessageDialog(None, message, title, style)
    dialog.ShowModal()
    dialog.Destroy()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, title='biwx', size=(820, 510))
    frame.Show()
    app.MainLoop()
