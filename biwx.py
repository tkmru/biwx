#!/usr/bin/env python2.7
# coding:UTF-8

import wx
import wx.grid as wxgrid
import wx.lib.agw.genericmessagedialog as wxgmd
import fy
#from multiprocessing import Process


GRID_LINE_COLOUR = '#e7daf7'
BACKGROUND_COLOUR = '#e8e8e8'
TEXT_COLOUR = '#252525'

ROW_SIZE = 20
ROW_LABEL_SIZE = 70
COL_LABEL_SIZE = 27

DUMP_FONT_SIZE = 12
HEX_FONT_SIZE = 13


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

        self.Bind(wx.EVT_SCROLLWIN, self._did_scroll)
        self.Bind(wx.EVT_MOUSEWHEEL, self._mousewheel)
        self.Bind(wx.EVT_SCROLLWIN_LINEUP, self._lineup_or_down)
        self.Bind(wx.EVT_SCROLLWIN_LINEDOWN, self._lineup_or_down)
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
        self._lineup_or_down()

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

    def _lineup_or_down(self, event=None):
        '''Event handler for pressing the up arrow or the down arrow.'''
        if event and event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        y_pos = self.GetViewStart()[1]
        self._bound_widget.scroll_to(y_pos)
        self.scroll_to(y_pos)

    def _did_scroll(self, event):
        '''Event handler for manual scrolling.'''
        try:
            if event.GetOrientation() != wx.VERTICAL or self._locked:
                return

            self._bound_widget.scroll_to(event.GetPosition())

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


class BinaryResource(object):

    def __init__(self):
        self.data = '57656c636f6d6520746f20626977782121'


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

    def __init__(self, resource):
        wxgrid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']

        self.resource = resource

        self.font_attr = wx.grid.GridCellAttr()
        self.font_attr.SetFont(wx.Font(DUMP_FONT_SIZE,  wx.DEFAULT, wx.NORMAL, wx.LIGHT, encoding=wx.FONTENCODING_SYSTEM))
        self.font_attr.SetTextColour(TEXT_COLOUR)

    def GetNumberRows(self):
        return 22

    def GetNumberCols(self):
        return 16

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # get initial value
        address = row * 32 + col*2
        if address+2 <= len(self.resource.data):
            ascii_number = int(self.resource.data[address: address+2], 16)

            if 0 <= ascii_number <= 32 or 127 <= ascii_number:
                return '.'

            else:
                return chr(ascii_number)

        else:
            return ''

    def SetValue(self, row, col, value): # change value
        address = row * 32 + col * 2
        hex_value = '{0:2x}'.format(ord(value))
        if address <= len(self.resource.data):
            self.resource.data = self.resource.data[:address] + hex_value + self.resource.data[address+2:]

        else:
            # not reflected
            self.resource.data = self.resource.data + '00'*(address-len(self.resource.data)) + hex_value + self.resource.data[address+2:]
        print self.resource.data

    def GetColLabelValue(self, col):
        return self.cols_labels[col]

    def GetAttr(self, row, col, kind):
        attr = self.font_attr
        attr.IncRef()
        return attr

    def append_rows(self, number):
        msg = wxgrid.GridTableMessage(self, wxgrid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
        self.GetView().ProcessTableMessage(msg)


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

    def __init__(self, resource):
        wxgrid.PyGridTableBase.__init__(self)

        self.cols_labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']

        self.resource = resource

        self.font_attr = wx.grid.GridCellAttr()
        self.font_attr.SetFont(wx.Font(HEX_FONT_SIZE,  wx.DEFAULT, wx.NORMAL, wx.LIGHT, encoding=wx.FONTENCODING_SYSTEM))
        self.font_attr.SetTextColour(TEXT_COLOUR)

    def GetNumberRows(self):
        return 22

    def GetNumberCols(self):
        return 16

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col): # get initial value
        address = row * 32 + col * 2
        if address+2 <= len(self.resource.data):
            return self.resource.data[address: address+2]

        else:
            return ''

    def SetValue(self, row, col, value): # change value
        address = row * 32 + col * 2
        if address <= len(self.resource.data):
            self.resource.data = self.resource.data[:address] + value[:2] + self.resource.data[address+2:]

        else:
            # not reflected
            self.resource.data = self.resource.data + '00'*(address-len(self.resource.data)) + value[:2] + self.resource.data[address+2:]
        print self.resource.data

    def GetColLabelValue(self, col):
        return self.cols_labels[col]

    def GetRowLabelValue(self, row):
        return '0x{0:0>6X}'.format(row * 16)

    def GetAttr(self, row, col, kind):
        attr = self.font_attr
        attr.IncRef()
        return attr

    def append_rows(self, number):
        msg = wxgrid.GridTableMessage(self, wxgrid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
        self.GetView().ProcessTableMessage(msg)


class Editor(wx.Panel):

    def __init__(self, *args, **kwags):
        wx.Panel.__init__(self, *args, **kwags)

        self.resource = BinaryResource()

        self.before_col = None
        self.before_row = None

        self.hex_grid = HexGrid(self)
        self.hex_table = HexGridTable(self.resource)
        self.hex_grid.SetTable(self.hex_table)
        self.hex_grid.Bind(wxgrid.EVT_GRID_SELECT_CELL, self.on_selected_cell)

        self.dump_grid = DumpGrid(self)
        self.dump_table = DumpGridTable(self.resource)
        self.dump_grid.SetTable(self.dump_table)
        self.dump_grid.Bind(wxgrid.EVT_GRID_SELECT_CELL, self.on_selected_cell)

        # Bind the scrollbars of the widgets.
        self.hex_grid.bind_scroll(self.dump_grid)
        self.dump_grid.bind_scroll(self.hex_grid)

        for i in range(0, 16):
            self.hex_grid.SetColSize(i, 30)

        for i in range(0, 16):
            self.dump_grid.SetColSize(i, 15)

        self.dump_grid.Refresh()
        self.hex_grid.Refresh()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.hex_grid, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=3)
        sizer.Add(self.dump_grid, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)

    def on_selected_cell(self, event):
        """
        Get the selection of a single cell by clicking or 
        moving the selection with the arrow keys
        """
        selected_row = event.GetRow()
        selected_col = event.GetCol()
        print selected_row, selected_col

        if self.before_col is not None and self.before_row is not None:
            old_attr = wxgrid.GridCellAttr()
            old_attr.SetBackgroundColour("#FFFFFF")
            old_attr.IncRef()
            self.hex_table.SetAttr(old_attr, self.before_row, self.before_col)

        attr = wxgrid.GridCellAttr()
        attr.SetBackgroundColour("#FFFFCC")
        attr.IncRef()
        self.hex_table.SetAttr(attr, selected_row, selected_col)

        self.hex_grid.ForceRefresh()
        print 'selected'
        event.Skip()

    def update_rows(self, new_binary):
        binary_length = len(new_binary)
        added_rows = binary_length / 32 - 21

        self.hex_table.binary_data = new_binary
        self.hex_table.binary_length = binary_length
        self.hex_table.append_rows(added_rows)
        self.hex_grid.ForceRefresh()

        self.dump_table.binary_data = new_binary
        self.dump_table.binary_length = binary_length
        self.dump_table.append_rows(added_rows)
        self.dump_grid.ForceRefresh()

    def load_file(self, file_path):
        try:
            new_binary = fy.get(file_path)
            self.update_rows(new_binary)
            self.resource.data = new_binary

        except Exception, e:
            print e
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
        file_menu.Append(wx.ID_SAVE, '&Save', 'Save current binary')

        # creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)  # adding the MenuBar to the Frame content.
        self.Connect(wx.ID_OPEN, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.open_file_dialog)
        self.Connect(wx.ID_SAVE, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.save_file)

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

    def save_file(self, event):
        target_path = self._file_dialog('Save a file', style=wx.SAVE)
        print target_path
        self.SetStatusText('Saved file "{0}".'.format(target_path))
        print self.editor.resource.data
        fy.write(target_path, self.editor.resource.data)


def message_box(message, title, style=wx.OK | wx.ICON_INFORMATION):
    dialog = wxgmd.GenericMessageDialog(None, message, title, style)
    dialog.ShowModal()
    dialog.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainWindow(None, title='biwx', size=(810, 510))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
