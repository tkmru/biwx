#!/usr/bin/env python3.7
# coding: UTF-8

import wx

ROW_SIZE = 20


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
