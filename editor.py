#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import wx.grid
import grids
import ui_parts
import fy

NORMAL_CELL_COLOUR = '#ffffff'
SELECTED_CELL_COLOUR = '#aff0fa'
FILE_SIGNATURE_COLOUR = '#ffe792'


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

        self.hex_grid = grids.HexGrid(self)
        self.hex_table = grids.HexGridTable(self.resource)
        self.hex_grid.SetTable(self.hex_table)
        self.hex_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_selected)
        self.hex_grid.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self.show_popup_on_hex_grid)

        self.dump_grid = grids.DumpGrid(self)
        self.dump_table = grids.DumpGridTable(self.resource)
        self.dump_grid.SetTable(self.dump_table)
        self.dump_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_selected)
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
            ui_parts.message_box('This file include hidden file.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

    def load_file(self, header_indexies, footer_indexies):
        try:
            self.remove_old_signature_cell_color()
            self.update_rows(self.resource.binary)
            self.change_signature_cell_color(header_indexies, footer_indexies)

            if fy.check_hidden_data(self.resource.binary, header_indexies, footer_indexies):
                ui_parts.message_box('This file include hidden file.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

        except Exception, e:
            print e
            ui_parts.message_box('Can not open file {0}.'.format(self.resource.file_path), 'Load File Error', wx.OK | wx.ICON_ERROR)
