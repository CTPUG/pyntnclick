# widgets.py
# Copyright Boomslang team, 2010 (see COPYING File)

"""Custom Albow widgets"""

import textwrap

import albow.controls
import albow.menu
from albow.resource import get_font, get_image
from pygame.color import Color
from pygame.rect import Rect

from constants import BUTTON_SIZE
from cursor import CursorWidget


class BoomLabel(albow.controls.Label):

    trim_line_top = 0

    def __init__(self, text, width=None, **kwds):
        albow.controls.Label.__init__(self, text, width, **kwds)
        w, h = self.size
        h -= self.trim_line_top * len(self.text.split('\n'))
        self.size = (w, h)

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

    def draw_with(self, surface, fg, _bg=None):
        m = self.margin
        align = self.align
        width = surface.get_width()
        y = m
        lines = self.text.split("\n")
        font = self.font
        dy = font.get_linesize() - self.trim_line_top
        for line in lines:
            image = font.render(line, True, fg)
            r = image.get_rect()
            image = image.subsurface(r.clip(r.move(0, self.trim_line_top)))
            r.top = y
            if align == 'l':
                r.left = m
            elif align == 'r':
                r.right = width - m
            else:
                r.centerx = width // 2
            surface.blit(image, r)
            y += dy


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
        self.screen.state.highlight_override = True


class MessageDialog(BoomLabel, CursorWidget):

    def __init__(self, screen, text, wrap_width, style=None, **kwds):
        CursorWidget.__init__(self, screen)
        self.set_style(style)
        paras = text.split("\n\n")
        text = "\n".join([textwrap.fill(para, wrap_width) for para in paras])
        BoomLabel.__init__(self, text, **kwds)

    def set_style(self, style):
        self.set_margin(5)
        self.border_width = 1
        self.border_color = (0, 0, 0)
        self.bg_color = (127, 127, 127)
        self.fg_color = (0, 0, 0)
        if style == "JIM":
            self.set(font=get_font(20, "Monospace.ttf"))
            self.trim_line_top = 10
            self.bg_color = Color(255, 127, 127, 207)
            self.fg_color = (0, 0, 0)
            self.border_color = (127, 0, 0)

    def draw_all(self, surface):
        BoomLabel.draw_all(self, surface)

    def _draw_all_no_bg(self, surface):
        CursorWidget.draw_all(self, surface)

    def mouse_down(self, event):
        self.dismiss()

    def cursor_highlight(self):
        return False


class HandButton(albow.controls.Image):
    """The fancy hand button for the widget"""

    def __init__(self, action):
        # FIXME: Yes, please.
        this_image = get_image('items', 'hand.png')
        albow.controls.Image.__init__(self, image=this_image)
        self.action = action
        self.set_rect(Rect(0, 0, BUTTON_SIZE, BUTTON_SIZE))

    def mouse_down(self, event):
        self.action()


class PopupMenuButton(albow.controls.Button):

    def __init__(self, text, action):
        albow.controls.Button.__init__(self, text, action)

        self.font = get_font(16, 'Vera.ttf')
        self.set_rect(Rect(0, 0, BUTTON_SIZE, BUTTON_SIZE))
        self.margin = (BUTTON_SIZE - self.font.get_linesize()) / 2


class PopupMenu(albow.menu.Menu, CursorWidget):

    def __init__(self, screen):
        CursorWidget.__init__(self, screen)
        self.screen = screen
        self.shell = screen.shell
        items = [
                ('Resume Game', 'hide'),
                ('Quit Game', 'quit'),
                ('Exit to Main Menu', 'main_menu'),
                ]
        # albow.menu.Menu ignores title string
        albow.menu.Menu.__init__(self, None, items)
        self.font = get_font(16, 'Vera.ttf')

    def show_menu(self):
        """Call present, with the correct position"""
        item_height = self.font.get_linesize()
        menu_top = 600 - (len(self.items) * item_height + BUTTON_SIZE)
        item = self.present(self.shell, (0, menu_top))
        if item > -1:
            # A menu item needs to be invoked
            self.invoke_item(item)

