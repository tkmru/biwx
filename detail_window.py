#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import string
import subprocess
import ui_parts
import pdfid_v0_2_1.pdfid


class DetailWindow(wx.Notebook):
    def __init__(self, *args, **kwags):
        wx.Notebook.__init__(self, *args, **kwags)

        self.signature_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.strings_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.pdf_parse_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.InsertPage(0, self.signature_textctrl, "signature")
        self.InsertPage(1, self.strings_textctrl, "strings")

    def load_file(self, file_path, header_indexies, footer_indexies):
        self.load_strings(file_path)
        self.display_signature(header_indexies, footer_indexies)
        if 'pdf' in file_path:
            self.InsertPage(2, self.pdf_parse_textctrl, "pdf-parse")
            self.pdfparse(file_path)
        print header_indexies, footer_indexies

    def load_strings(self, file_path):
        for s in strings(file_path):
            self.strings_textctrl.AppendText(s)

    def display_signature(self, header_indexies, footer_indexies):
        self.signature_textctrl.AppendText('HEADER\n')
        for key in header_indexies.keys():
            self.signature_textctrl.AppendText(key + ': ' + str(len(header_indexies[key])) + 'signature\n')

        self.signature_textctrl.AppendText('\nFOOTER\n')
        for key in footer_indexies.keys():
            self.signature_textctrl.AppendText(key + ': ' + str(len(footer_indexies[key])) + 'signature\n')

    def pdfparse(self, file_path):
        result = subprocess.check_output(['python', 'pdf-parser.py', file_path])
        if 'JavaScript' in result:
            ui_parts.message_box('This PDF include JavaScript code.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

        self.pdf_parse_textctrl.AppendText(result)


def strings(filename, min=4):
    with open(filename, "rb") as f:
        result = ""
        for c in f.read():
            if c in string.printable:
                result += c
                continue
            if len(result) >= min:
                yield result
            result = ""
