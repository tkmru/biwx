#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import string


class DetailWindow(wx.Notebook):
    def __init__(self, *args, **kwags):
        wx.Notebook.__init__(self, *args, **kwags)

        self.signature_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.strings_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.pdf_parse_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.InsertPage(0, self.signature_textctrl, "signature")
        self.InsertPage(1, self.strings_textctrl, "strings")
        self.InsertPage(2, self.pdf_parse_textctrl, "pdf-parse")

    def load_strings(self, file_path):
        for s in strings(file_path):
            self.strings_textctrl.AppendText(s)

    def load_file(self, file_path):
        self.load_strings(file_path)


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
