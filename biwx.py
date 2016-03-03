#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import wx.grid
import wx.lib.dialogs as wxdialogs
import editor
import detail_window
import fy
import sys
import os
# from multiprocessing import Process

BACKGROUND_COLOUR = '#e8e8e8'


class MainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.CreateStatusBar() # a Statusbar in the bottom of the window
        ID_AUTO_EXTRACT = wx.NewId()
        ID_EXTRACT_FROM_PDF = wx.NewId()

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
        analysis_menu.Append(ID_AUTO_EXTRACT, '&Auto extract embedded file', 'Auto extract embedded file')
        self.Connect(ID_AUTO_EXTRACT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.extract_files)
        analysis_menu.Append(ID_EXTRACT_FROM_PDF, '&Extract JavaScript code from pdf', 'Extract JavaScript code from pdf')
        self.Connect(ID_EXTRACT_FROM_PDF, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.extract_js_from_pdf)
        menu_bar.Append(analysis_menu, '&Analysis')

        # adding the MenuBar to the Frame content.
        self.SetMenuBar(menu_bar)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.detail_window = detail_window.DetailWindow(self)
        sizer.Add(self.detail_window, proportion=1, flag=wx.EXPAND)
        self.editor = editor.Editor(self)
        sizer.Add(self.editor, proportion=1, flag=wx.EXPAND)

        self.SetSizer(sizer)

        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.editor.hex_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.display_address)
        self.editor.dump_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.display_address)

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
        source_path = self.editor.resource.file_path
        if source_path is not None:
            target_path = os.path.split(source_path)[0] + '/result'
            extract_files = fy.extract(source_path, target_path)

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

    def extract_js_from_pdf(self, event):
        pass

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
            new_binary_string = fy.get(file_path)
            header_indexies = fy.get_signature_index(new_binary_string, fy.headers)
            footer_indexies = fy.get_signature_index(new_binary_string, fy.footers)

            self.editor.resource.file_path = file_path
            self.editor.resource.binary = new_binary_string
            self.editor.load_file(header_indexies, footer_indexies)

            self.detail_window.load_file(file_path, header_indexies, footer_indexies) # heavy

            self.SetTitle(file_path)
            self.SetStatusText('Opened file "{0}".'.format(file_path.encode('utf-8')))

    def save_file(self, event):
        target_path = self._file_dialog('Save a file', style=wx.SAVE)
        self.SetStatusText('Saved file "{0}".'.format(target_path))
        try:
            fy.write(target_path, self.editor.resource.binary)

        except TypeError: # target_path is empty, when cancel button click.
            pass


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainWindow(None, title='biwx', size=(1130, 550))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
