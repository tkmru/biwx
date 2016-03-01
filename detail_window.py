#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import string
import subprocess
import ui_parts
import pdfid_v0_2_1.pdfid as pdfidlib


class DetailWindow(wx.Notebook):
    def __init__(self, *args, **kwags):
        wx.Notebook.__init__(self, *args, **kwags)

        self.signature_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.strings_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.pdfid_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.pdf_parse_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.InsertPage(0, self.signature_textctrl, "signature")
        self.InsertPage(1, self.strings_textctrl, "strings")

    def load_file(self, file_path, header_indexies, footer_indexies):
        self.load_strings(file_path)
        self.display_signature(header_indexies, footer_indexies)
        if 'pdf' in file_path:
            self.InsertPage(2, self.pdfid_textctrl, "pdfid")
            self.InsertPage(3, self.pdf_parse_textctrl, "pdf-parse")
            self.display_pdfid(file_path)
            self.display_pdfparse(file_path)

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

    def display_pdfid(self, file_path):
        pdfid = get_pdfid_value(file_path)
        self.pdfid_textctrl.AppendText(pdfid)

    def display_pdfparse(self, file_path):
        result = subprocess.check_output(['python', 'pdf-parser.py', '--filter', '--raw', file_path])
        JS_start = result.find('</JavaScript')
        JS_end = result.find('/JavaScript>') + len('/JavaScript>')

        if 'JavaScript' in result:
            ui_parts.message_box('This PDF include JavaScript code.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

        self.pdf_parse_textctrl.AppendText(result[JS_start: JS_end])


def get_pdfid_value(filename):
    xmlDoc = pdfidlib.PDFiD(filename)
    header = 'PDF Header: {0}\n'.format(xmlDoc.documentElement.getAttribute('Header'))
    pdfid = ''
    for node in xmlDoc.documentElement.getElementsByTagName('Keywords')[0].childNodes:
        pdfid += '{0:<10}{1: 5d}\n'.format(node.getAttribute('Name'), int(node.getAttribute('Count')))

    return header + pdfid


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
