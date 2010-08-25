# widgets.py
# Copyright Boomslang team, 2010 (see COPYING File)

"""Custom Albow widgets"""

import textwrap

import albow.controls

from cursor import CursorWidget


class BoomLabel(albow.controls.Label):

    def set_margin(self, margin):
        """Add a set_margin method that recalculates the label size"""
        old_margin = self.margin
        w, h = self.size
        d = margin - old_margin
        self.margin = margin
        self.size = (w + 2 * d, h + 2 * d)


class MessageDialog(BoomLabel, CursorWidget):

    def __init__(self, screen, text, wrap_width, **kwds):
        CursorWidget.__init__(self, screen)
        paras = text.split("\n\n")
        text = "\n".join([textwrap.fill(para, wrap_width) for para in paras])
        albow.controls.Label.__init__(self, text, **kwds)
        self.set_margin(5)
        self.border_width = 1
        self.border_color = (0, 0, 0)
        self.bg_color = (127, 127, 127)
        self.fg_color = (0, 0, 0)

    def mouse_down(self, event):
        self.dismiss()
