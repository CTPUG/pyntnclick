# widgets.py
# Copyright Boomslang team, 2010 (see COPYING File)

"""Custom Albow widgets"""

import textwrap

import albow.controls
from pygame.color import Color
from pygame.locals import BLEND_ADD

from cursor import CursorWidget


class BoomLabel(albow.controls.Label):

    def set_margin(self, margin):
        """Add a set_margin method that recalculates the label size"""
        old_margin = self.margin
        w, h = self.size
        d = margin - old_margin
        self.margin = margin
        self.size = (w + 2 * d, h + 2 * d)

    def draw_all(self, surface):
        bg_color = self.bg_color
        self.bg_color = None
        if bg_color is not None:
            new_surface = surface.convert_alpha()
            new_surface.fill(bg_color)
            surface.blit(new_surface, surface.get_rect())
        albow.controls.Label.draw_all(self, surface)
        self._draw_all_no_bg(surface)
        self.bg_color = bg_color

    def _draw_all_no_bg(self, surface):
        pass


class MessageDialog(BoomLabel, CursorWidget):

    def __init__(self, screen, text, wrap_width, style=None, **kwds):
        CursorWidget.__init__(self, screen)
        paras = text.split("\n\n")
        text = "\n".join([textwrap.fill(para, wrap_width) for para in paras])
        albow.controls.Label.__init__(self, text, **kwds)
        self.set_style(style)

    def set_style(self, style):
        self.set_margin(5)
        self.border_width = 1
        self.border_color = (0, 0, 0)
        self.bg_color = (127, 127, 127)
        self.fg_color = (0, 0, 0)
        if style == "JIM":
            self.bg_color = Color(127, 0, 0, 191)
            self.fg_color = (0, 0, 0)
            self.border_color = (255, 0, 0)

    def draw_all(self, surface):
        BoomLabel.draw_all(self, surface)

    def _draw_all_no_bg(self, surface):
        CursorWidget.draw_all(self, surface)

    def mouse_down(self, event):
        self.dismiss()
