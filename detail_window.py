#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import string
import subprocess
import ui_parts
import pdfid_v0_2_5.pdfid as pdfidlib
from multiprocessing import Queue, Process


class DetailWindow(wx.Notebook):
    def __init__(self, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)

        self.signature_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.strings_queue = Queue()
        self.strings_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.pdfid_queue = Queue()
        self.pdfid_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        self.pdf_parse_queue = Queue()
        self.pdf_parse_textctrl = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.Bind(wx.EVT_IDLE, self.on_idle)

        self.InsertPage(0, self.signature_textctrl, "signature")
        self.InsertPage(1, self.strings_textctrl, "strings")

    def on_idle(self, event):
        if not self.strings_queue.empty():
            self.strings_textctrl.WriteText(self.strings_queue.get() + '\n')

        if not self.pdfid_queue.empty():
            pdfid_tuple = self.pdfid_queue.get()
            index = pdfid_tuple[0]
            pdfid = pdfid_tuple[1]
            self.pdfid_textctrl.AppendText(pdfid)
            if pdfid.startswith('/JS') or pdfid.startswith('/JavaScript') or pdfid.startswith('/ObjStm'):
                self.pdfid_textctrl.SetStyle(21*(index), 21*(index+1), wx.TextAttr("RED", "White"))

        if not self.pdf_parse_queue.empty():
            result = self.pdf_parse_queue.get()
            if 'JavaScript' in result:
                ui_parts.message_box('This PDF include JavaScript code.', 'Hidden File Alert', wx.OK | wx.ICON_ERROR)

            self.pdf_parse_textctrl.WriteText(result + '\n')

    def load_file(self, file_path, header_indexies, footer_indexies):
        self.clear_window()
        self.start_puts_strings(file_path)
        self.display_signature(header_indexies, footer_indexies)
        if 'pdf' in file_path:
            self.InsertPage(2, self.pdfid_textctrl, "pdfid")
            self.InsertPage(3, self.pdf_parse_textctrl, "pdf-parse")
            self.start_puts_pdfid(file_path)
            self.start_puts_pdf_parse(file_path)

    def clear_window(self):
        self.signature_textctrl.Clear()
        self.strings_textctrl.Clear()
        self.pdfid_textctrl.Clear()
        self.pdf_parse_textctrl.Clear()

    def start_puts_strings(self, file_path):
        p = Process(target=self.convert_strings, args=(file_path,))
        p.start()

    def convert_strings(self, file_path):
        for s in strings(file_path):
            self.strings_queue.put(s)

    def display_signature(self, header_indexies, footer_indexies):
        self.signature_textctrl.AppendText('HEADER\n')
        for key in header_indexies.keys():
            self.signature_textctrl.AppendText(key + ': ' + str(len(header_indexies[key])) + 'signature\n')

        self.signature_textctrl.AppendText('\nFOOTER\n')
        for key in footer_indexies.keys():
            self.signature_textctrl.AppendText(key + ': ' + str(len(footer_indexies[key])) + 'signature\n')

    def start_puts_pdfid(self, file_path):
        p = Process(target=self.load_pdfid, args=(file_path,))
        p.start()

    def load_pdfid(self, file_path):
        for i, pdfid in enumerate(get_pdfid_value(file_path)):
            self.pdfid_queue.put((i, pdfid))

    def start_puts_pdf_parse(self, file_path):
        p = Process(target=self.load_pdf_parse, args=(file_path,))
        p.start()

    def load_pdf_parse(self, file_path):
        result = subprocess.check_output(['python', 'pdf-parser.py', '--filter', '--raw', file_path])
        JS_start = result.find('</JavaScript')
        JS_end = result.find('/JavaScript>') + len('/JavaScript>')
        result = result[JS_start: JS_end].replace('>>', '>>\n').replace('\\r', '\n').replace('\\', '')
        self.pdf_parse_queue.put(result)


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