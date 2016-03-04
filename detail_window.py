#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import string
import subprocess
import ui_parts
import pdfid_v0_2_1.pdfid as pdfidlib
from multiprocessing import Queue, Process


class DetailWindow(wx.Notebook):
    def __init__(self, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)

        self.signature_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.strings_queue = Queue()
        self.strings_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.pdfid_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        self.pdf_parse_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.Bind(wx.EVT_IDLE, self.on_idle)

        self.InsertPage(0, self.signature_textctrl, "signature")
        self.InsertPage(1, self.strings_textctrl, "strings")

    def on_idle(self, event):
        if not self.strings_queue.empty():
            self.strings_textctrl.AppendText(self.strings_queue.get() + '\n')

    def load_file(self, file_path, header_indexies, footer_indexies):
        self.clear_window()
        self.display_strings(file_path)
        self.display_signature(header_indexies, footer_indexies)
        if 'pdf' in file_path:
            self.InsertPage(2, self.pdfid_textctrl, "pdfid")
            self.InsertPage(3, self.pdf_parse_textctrl, "pdf-parse")
            self.display_pdfid(file_path)
            self.display_pdfparse(file_path)

    def clear_window(self):
        self.signature_textctrl.Clear()
        self.strings_textctrl.Clear()
        self.pdfid_textctrl.Clear()
        self.pdf_parse_textctrl.Clear()

    def display_strings(self, file_path):
        for s in strings(file_path):
            self.strings_queue.put(s)

    def display_signature(self, header_indexies, footer_indexies):
        self.signature_textctrl.AppendText('HEADER\n')
        for key in header_indexies.keys():
            self.signature_textctrl.AppendText(key + ': ' + str(len(header_indexies[key])) + 'signature\n')

        self.signature_textctrl.AppendText('\nFOOTER\n')
        for key in footer_indexies.keys():
            self.signature_textctrl.AppendText(key + ': ' + str(len(footer_indexies[key])) + 'signature\n')

    def display_pdfid(self, file_path):
        for i, pdfid in enumerate(get_pdfid_value(file_path)):
            self.pdfid_textctrl.AppendText(pdfid)
            if pdfid.startswith('/JS') or pdfid.startswith('/JavaScript') or pdfid.startswith('/ObjStm'):
                self.pdfid_textctrl.SetStyle(21*(i-1), 21*i, wx.TextAttr("RED", "White"))

    def display_pdfparse(self, file_path):
        result = subprocess.check_output(['python', 'pdf-parser.py', '--filter', '--raw', file_path])
        JS_start = result.find('</JavaScript')
        JS_end = result.find('/JavaScript>') + len('/JavaScript>')

        if 'JavaScript' in result:
            ui_parts.message_box('This PDF include JavaScript code.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

        self.pdf_parse_textctrl.AppendText(result[JS_start: JS_end].replace('>>', '>>\n').replace('\\r', '\n').replace('\\', ''))


def get_pdfid_value(filename):
    xmlDoc = pdfidlib.PDFiD(filename)
    header = 'PDF Header: {0}\n'.format(xmlDoc.documentElement.getAttribute('Header'))
    yield header
    for node in xmlDoc.documentElement.getElementsByTagName('Keywords')[0].childNodes:
        yield '{0: <15}{1: 5d}\n'.format(node.getAttribute('Name'), int(node.getAttribute('Count')))


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
