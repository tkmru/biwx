#!/usr/bin/env python2.7
# coding:UTF-8

import wx
import wx.grid as wxgrid
import wx.lib.agw.genericmessagedialog as wxgmd
import wx.lib.dialogs as wxdialogs
import fy
import sys
# from multiprocessing import Process


GRID_LINE_COLOUR = '#e7daf7'
BACKGROUND_COLOUR = '#e8e8e8'
NORMAL_CELL_COLOUR = '#ffffff'
SELECTED_CELL_COLOUR = '#aff0fa'
FILE_SIGNATURE_COLOUR = '#ffe792'

ROW_SIZE = 20
ROW_LABEL_SIZE = 70
COL_LABEL_SIZE = 27

DUMP_FONT_SIZE = 12
HEX_FONT_SIZE = 13


class ScrollBinder(object):

    '''
    http://wxpython-users.1045709.n5.nabble.com/Scrolling-grids-simultaneously-td2349695.html
    Inherit to be able to bind scrolling to another widget.
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
        self.Bind(wx.EVT_CHAR_HOOK, self._key_down)

    def bind_scroll(self, target):
        self._bound_widget = target # another grid

    def _key_down(self, event):
        '''for the up arrow key and the down arrow key'''
        keycode = event.GetKeyCode()
        y_pos = self.GetViewStart()[1]
        if keycode == wx.WXK_DOWN:
            self._bound_widget.scroll_to(y_pos+1)
            self.scroll_to(y_pos+1)
        elif keycode == wx.WXK_UP:
            self._bound_widget.scroll_to(y_pos-1)
            self.scroll_to(y_pos-1)
        else:
            event.Skip()

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

        pos = 0
        self._bound_widget.scroll_to(pos)
        self.scroll_to(pos)

    def _bottom(self, event):
        '''Event handler for going to the bottom.'''
        if event.GetOrientation() != wx.VERTICAL:
            event.Skip()
            return

        pos = 10000000
        self._bound_widget.scroll_to(pos)
        self.scroll_to(pos)

    def _lineup_or_down(self, event=None):
        '''Event handler for trackpad.'''
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


class Resource(object):

    def __init__(self):
        self.file_path = None
        self.binary = '57656c636f6d6520746f20626977782121'

    def insert(self, row, col, hex_value):
        address = row * 32 + col * 2
        if address <= len(self.binary):
            self.binary = self.binary[:address] + hex_value + self.binary[address+2:]

        else:
            # not reflected
            self.binary = self.binary + '00'*(address-len(self.binary)) + hex_value + self.binary[address+2:]


class DumpGrid(wxgrid.Grid, ScrollBinder):

    def __init__(self, parent):
        wxgrid.Grid.__init__(self, parent, -1)
        ScrollBinder.__init__(self)
        self.SetGridLineColour(GRID_LINE_COLOUR)
        self.SetColLabelSize(COL_LABEL_SIZE)
        self.HideRowLabels()
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # http://stackoverflow.com/questions/4852972/wxpython-wxgrid-without-vertical-scrollbar
        self.ShowScrollbars(wx.SHOW_SB_DEFAULT, wx.SHOW_SB_NEVER)

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
        msg = wxgrid.GridTableMessage(self, wxgrid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
        self.GetView().ProcessTableMessage(msg)


class HexGrid(wxgrid.Grid, ScrollBinder):

    def __init__(self, parent):
        wxgrid.Grid.__init__(self, parent, -1)
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
        msg = wxgrid.GridTableMessage(self, wxgrid.GRIDTABLE_NOTIFY_ROWS_APPENDED, number)
        self.GetView().ProcessTableMessage(msg)


class Editor(wx.Panel):

    def __init__(self, *args, **kwags):
        wx.Panel.__init__(self, *args, **kwags)

        self.resource = Resource()

        self.selected_flag = 0
        self.arg_flag = 0
        self.old_selected_row = None
        self.old_selected_col = None
        self.old_selected_cell_color = None
        self.header_indexies = None
        self.footer_indexies = None

        self.hex_grid = HexGrid(self)
        self.hex_table = HexGridTable(self.resource)
        self.hex_grid.SetTable(self.hex_table)
        self.hex_grid.Bind(wxgrid.EVT_GRID_SELECT_CELL, self.on_cell_selected)
        self.hex_grid.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self.show_popup_on_hex_grid)

        self.dump_grid = DumpGrid(self)
        self.dump_table = DumpGridTable(self.resource)
        self.dump_grid.SetTable(self.dump_table)
        self.dump_grid.Bind(wxgrid.EVT_GRID_SELECT_CELL, self.on_cell_selected)
        self.dump_grid.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self.show_popup_on_dump_grid)

        # Bind the scrollbars of the widgets.
        self.hex_grid.bind_scroll(self.dump_grid)
        self.dump_grid.bind_scroll(self.hex_grid)

        self.popupmenu = wx.Menu()
        item = self.popupmenu.Append(wx.ID_ANY, 'Copy hex')
        self.Bind(wx.EVT_MENU, self.on_popup_selected, item)
        item = self.popupmenu.Append(wx.ID_ANY, 'Copy ascii')
        self.Bind(wx.EVT_MENU, self.on_popup_selected, item)
        self.ID_HEX = wx.NewId()
        self.popupmenu.Append(self.ID_HEX, 'Hex')
        self.ID_DECIMAL = wx.NewId()
        self.popupmenu.Append(self.ID_DECIMAL, 'Decimal')
        self.ID_BINARY = wx.NewId()
        self.popupmenu.Append(self.ID_BINARY, 'Binary')
        self.ID_ASCII = wx.NewId()
        self.popupmenu.Append(self.ID_ASCII, 'Ascii')

        for i in range(0, 16):
            self.hex_grid.SetColSize(i, 30)

        for i in range(0, 16):
            self.dump_grid.SetColSize(i, 15)

        self.dump_grid.Refresh()
        self.hex_grid.Refresh()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.hex_grid, flag=wx.EXPAND | wx.RIGHT, border=3)
        sizer.Add(self.dump_grid, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=10)
        self.SetSizerAndFit(sizer)

    def on_popup_selected(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetText()
        wx.MessageBox("You selected item '%s'" % text)

    def make_popup(self):
        self.popupmenu.Remove(self.ID_HEX)
        self.popupmenu.Remove(self.ID_DECIMAL)
        self.popupmenu.Remove(self.ID_BINARY)
        self.popupmenu.Remove(self.ID_ASCII)

        cell_hex = self.hex_grid.GetCellValue(self.old_selected_row, self.old_selected_col)
        if cell_hex == '':
            self.popupmenu.Append(self.ID_HEX, 'Hex: ')
            self.popupmenu.Append(self.ID_BINARY, 'Binary: ')
            self.popupmenu.Append(self.ID_DECIMAL, 'Decimal: ')
            self.popupmenu.Append(self.ID_ASCII, 'Ascii: ')
        else:
            cell_decimal = int(cell_hex, 16)
            self.popupmenu.Append(self.ID_HEX, 'Hex: 0x'+cell_hex)
            self.popupmenu.Append(self.ID_BINARY, 'Binary: '+str(bin(cell_decimal)))
            self.popupmenu.Append(self.ID_DECIMAL, 'Decimal: '+str(cell_decimal))
            try:
                cell_ascii = chr(cell_decimal)
                self.popupmenu.Append(self.ID_ASCII, 'Ascii: '+cell_ascii)

            except UnicodeDecodeError:
                cell_ascii = ''
                self.popupmenu.Append(self.ID_ASCII, 'Ascii: '+cell_ascii)

    def show_popup_on_hex_grid(self, event):
        # event.GetEventObject
        self.make_popup()
        pos = event.GetPosition()
        self.hex_grid.PopupMenu(self.popupmenu, (pos[0]+90, pos[1]+50))
        event.Skip()

    def show_popup_on_dump_grid(self, event):
        # event.GetEventObject
        self.make_popup()
        pos = event.GetPosition()
        self.dump_grid.PopupMenu(self.popupmenu, (pos[0]+14, pos[1]+50))
        event.Skip()

    def on_mouse_over(self, event):
        print 'mouse over'
        event.Skip()

    def on_cell_changed(self, event):
        self.hex_grid.ForceRefresh() # for being reflected edited data
        self.dump_grid.ForceRefresh() # for being reflected edited data

        print 'changed'
        event.Skip()

    def on_cell_selected(self, event):
        """
        Get the selection of a single cell by clicking or
        moving the selection with the arrow keys
        """

        if self.arg_flag == 0:
            if self.selected_flag == 1:
                self.change_cell_color(self.old_selected_row, self.old_selected_col, self.old_selected_cell_color)
            self.selected_flag = 1

            selected_row = event.GetRow()
            selected_col = event.GetCol()

            self.old_selected_row = selected_row
            self.old_selected_col = selected_col
            self.old_selected_cell_color = self.hex_grid.GetOrCreateCellAttr(selected_row, selected_col).GetBackgroundColour()

            self.change_cell_color(selected_row, selected_col, SELECTED_CELL_COLOUR)

            self.hex_grid.ForceRefresh() # for being reflected edited data
            self.dump_grid.ForceRefresh() # for being reflected edited data
            print 'selected' + hex(selected_col+16*selected_row)

        event.Skip()

    def change_cell_color(self, row, col, color):
        attr = self.hex_grid.GetOrCreateCellAttr(row, col)
        attr.SetBackgroundColour(color)
        self.hex_table.SetAttr(attr, row, col)

        attr = self.dump_grid.GetOrCreateCellAttr(row, col)
        attr.SetBackgroundColour(color)
        self.dump_table.SetAttr(attr, row, col)

    def remove_old_signature_cell_color(self):
        if self.header_indexies is not None:
            for file_type, indexies in self.header_indexies.items():
                for index in indexies:
                    for i in range(index[0]/2, (index[1]+1)/2):
                        self.change_cell_color(i/16, i % 16, NORMAL_CELL_COLOUR)

        if self.footer_indexies is not None:
            for file_type, indexies in self.footer_indexies.items():
                for index in indexies:
                    for i in range(index[0]/2, (index[1]+1)/2):
                        self.change_cell_color(i/16, i % 16, NORMAL_CELL_COLOUR)

    def change_signature_cell_color(self, header_indexies, footer_indexies):
        selected_cell = None
        if self.selected_flag == 1:
            # save selected cell color before change
            selected_cell = self.hex_grid.GetOrCreateCellAttr(self.old_selected_row, self.old_selected_col)
            selected_cell_color = selected_cell.GetBackgroundColour()

        for file_type, indexies in header_indexies.items():
            for index in indexies:
                for i in range(index[0]/2, (index[1]+1)/2):
                    self.change_cell_color(i/16, i % 16, FILE_SIGNATURE_COLOUR)

        for file_type, indexies in footer_indexies.items():
            for index in indexies:
                for i in range(index[0]/2, (index[1]+1)/2):
                    self.change_cell_color(i/16, i % 16, FILE_SIGNATURE_COLOUR)

        if self.selected_flag == 1:
            # restore selected cell color after change
            changed_selected_cell_color = selected_cell.GetBackgroundColour()
            if changed_selected_cell_color != (255, 255, 255) and changed_selected_cell_color != (175, 240, 250, 255):
                # when select cell color change
                self.old_selected_cell_color = selected_cell.GetBackgroundColour() # update because cell color change
                self.change_cell_color(self.old_selected_row, self.old_selected_col, selected_cell_color)

    def update_rows(self, new_binary):
        binary_length = len(new_binary)
        rows_number = binary_length / 32
        added_rows = rows_number - 21

        self.hex_table.binary_data = new_binary
        self.hex_table.binary_length = binary_length
        self.hex_table.append_rows(added_rows)
        self.hex_grid.ForceRefresh()

        self.dump_table.binary_data = new_binary
        self.dump_table.binary_length = binary_length
        self.dump_table.append_rows(added_rows)
        self.dump_grid.ForceRefresh()

    def check_hidden_data(self, binary_string, header_indexies, footer_indexies):
        if fy.check_hidden_data(binary_string, header_indexies, footer_indexies):
            message_box('This file include hidden file.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

    def load_file(self, file_path):
        try:
            self.remove_old_signature_cell_color()

            new_binary_string = fy.get(file_path)
            self.resource.file_path = file_path
            self.update_rows(new_binary_string)
            self.resource.binary = new_binary_string
            header_indexies = fy.get_signature_index(new_binary_string, fy.headers)
            footer_indexies = fy.get_signature_index(new_binary_string, fy.footers)
            self.change_signature_cell_color(header_indexies, footer_indexies)

            if fy.check_hidden_data(new_binary_string, header_indexies, footer_indexies):
                message_box('This file include hidden file.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

        except Exception, e:
            print e
            message_box('Can not open file {0}.'.format(file_path), 'Load File Error', wx.OK | wx.ICON_ERROR)


class DetailWindow(wx.Notebook):
    def __init__(self, *args, **kwags):
        wx.Notebook.__init__(self, *args, **kwags)

        panel_1 = wx.Panel(self, wx.ID_ANY)
        panel_2 = wx.Panel(self, wx.ID_ANY)
        panel_3 = wx.Panel(self, wx.ID_ANY)

        panel_1.SetBackgroundColour("#F0FFFF")
        panel_2.SetBackgroundColour("#FFF0FF")
        panel_3.SetBackgroundColour("#FFFFF0")

        self.InsertPage(0, panel_1, "tab_1")
        self.InsertPage(1, panel_2, "tab_2")
        self.InsertPage(2, panel_3, "tab_3")


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.CreateStatusBar() # a Statusbar in the bottom of the window
        ID_AUTO_EXTRACT = wx.NewId()

        # creating the menubar.
        menu_bar = wx.MenuBar()

        # on OSX Cocoa both the about and the quit menu belong to the bold 'app menu'.
        file_menu = wx.Menu() # setting up the menu.
        file_menu.Append(wx.ID_ABOUT, '&About', 'Information about this program')
        file_menu.Append(wx.ID_PREFERENCES, '&Preferences')
        file_menu.Append(wx.ID_EXIT, '&Exit', 'Terminate the program')
        file_menu.Append(wx.ID_NEW, '&New Window', 'Open new window')
        file_menu.Append(wx.ID_OPEN, '&Open', 'Open file')
        file_menu.Append(wx.ID_SAVE, '&Save', 'Save current binary')
        self.Connect(wx.ID_OPEN, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.open_file_dialog)
        self.Connect(wx.ID_SAVE, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.save_file)
        menu_bar.Append(file_menu, '&File')

        analysis_menu = wx.Menu() # setting up the menu.
        analysis_menu.Append(ID_AUTO_EXTRACT, '&Auto extract', 'Auto extract embedded file')
        self.Connect(ID_AUTO_EXTRACT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.extract_files)
        menu_bar.Append(analysis_menu, '&Analysis')

        # adding the MenuBar to the Frame content.
        self.SetMenuBar(menu_bar)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.detail_window = DetailWindow(self)
        sizer.Add(self.detail_window, proportion=1, flag=wx.EXPAND)
        self.editor = Editor(self)
        sizer.Add(self.editor, proportion=1, flag=wx.EXPAND)

        self.SetSizer(sizer)

        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.editor.hex_grid.Bind(wxgrid.EVT_GRID_SELECT_CELL, self.display_address)
        self.editor.dump_grid.Bind(wxgrid.EVT_GRID_SELECT_CELL, self.display_address)

        try: # if command line arg exist. ex) biwx.py [filename]
            file_path = sys.argv[1]
            if file_path is not None:
                self.editor.arg_flag = 1
                self.editor.load_file(file_path)
                self.SetTitle(file_path)
                self.SetStatusText('Opened file "{0}".'.format(file_path))
                self.editor.arg_flag = 0

        except IndexError:
            pass

    def extract_files(self, event):
        target_path = self.editor.resource.file_path
        if target_path is not None:
            extract_files = fy.extract(target_path, 'result')

            # create message on dialog
            result = ''
            for file_type, path_list in extract_files.items():
                result += 'extract {0} {1} files.\n'.format(len(extract_files)+1, file_type)
                for path in path_list:
                    result += path+'\n'
                result += '\n'

            dlg = wxdialogs.ScrolledMessageDialog(self, result, "extract files")
            dlg.ShowModal()
            dlg.Destroy()

    def display_address(self, event):
        selected_row = event.GetRow()
        selected_col = event.GetCol()
        hex_value = self.editor.hex_grid.GetCellValue(selected_row, selected_col)
        if hex_value != '':
            hex_value = '0x' + hex_value
        dump_value = self.editor.dump_grid.GetCellValue(selected_row, selected_col)
        self.SetStatusText('address: 0x{0:0>6X},   hex value: {1},   dump value: {2}'.format(selected_col+16*selected_row, hex_value, dump_value))
        event.Skip()

    def _file_dialog(self, *args, **kwargs):
        dialog = wx.FileDialog(self, *args, **kwargs)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            dialog.Destroy()

            return file_path

        dialog.Destroy()

    def open_file_dialog(self, event):
        file_path = self._file_dialog('Load a file', style=wx.OPEN)
        if file_path is not None:
            self.editor.load_file(file_path)
            self.SetTitle(file_path)
            self.SetStatusText('Opened file "{0}".'.format(file_path.encode('utf-8')))

    def save_file(self, event):
        target_path = self._file_dialog('Save a file', style=wx.SAVE)
        self.SetStatusText('Saved file "{0}".'.format(target_path))
        try:
            fy.write(target_path, self.editor.resource.binary)

        except TypeError: # target_path is empty, when cancel button click.
            pass


def message_box(message, title, style=wx.OK | wx.ICON_INFORMATION):
    dialog = wxgmd.GenericMessageDialog(None, message, title, style)
    dialog.ShowModal()
    dialog.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainWindow(None, title='biwx', size=(1050, 510))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
