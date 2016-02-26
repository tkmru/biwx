#!/usr/bin/env python2.7
# coding: UTF-8

import wx
import wx.lib.agw.genericmessagedialog as wxgmd


def message_box(message, title, style=wx.OK | wx.ICON_INFORMATION):
    dialog = wxgmd.GenericMessageDialog(None, message, title, style)
    dialog.ShowModal()
    dialog.Destroy()
