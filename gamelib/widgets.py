# widgets.py
# Copyright Boomslang team, 2010 (see COPYING File)

"""Custom Albow widgets"""

import textwrap

import albow.controls
from albow.resource import get_font
from pygame.color import Color

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

class BoomButton(BoomLabel):

    def __init__(self, text, action, screen):
        super(BoomLabel, self).__init__(text, font=get_font(20, 'Vera.ttf'))
        self.bg_color = (0, 0, 0)
        self.action = action
        self.screen = screen

    def mouse_down(self, event):
        self.action()
        self.screen.state_widget.mouse_move(event)

    def mouse_move(self, event):
        pos = self.parent.global_to_local(event.pos)
        if self.rect.collidepoint(pos):
            self.screen.cursor_highlight(True)


class MessageDialog(BoomLabel, CursorWidget):

    def __init__(self, screen, text, wrap_width, style=None, **kwds):
        CursorWidget.__init__(self, screen)
        self.set_style(style)
        paras = text.split("\n\n")
        text = "\n".join([textwrap.fill(para, wrap_width) for para in paras])
        albow.controls.Label.__init__(self, text, **kwds)

    def set_style(self, style):
        self.set_margin(5)
        self.border_width = 1
        self.border_color = (0, 0, 0)
        self.bg_color = (127, 127, 127)
        self.fg_color = (0, 0, 0)
        if style == "JIM":
            self.set(font=get_font(20, "chintzy.ttf"))
            self.bg_color = Color(255, 127, 127, 207)
            self.fg_color = (0, 0, 0)
            self.border_color = (127, 0, 0)

    def draw_all(self, surface):
        BoomLabel.draw_all(self, surface)

    def _draw_all_no_bg(self, surface):
        CursorWidget.draw_all(self, surface)

    def mouse_down(self, event):
        self.dismiss()
