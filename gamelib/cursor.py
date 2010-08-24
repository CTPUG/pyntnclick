# cursor.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Sprite Cursor

from albow.widget import Widget
from albow.resource import get_image
import pygame.mouse as mouse
from pygame.sprite import Sprite, RenderUpdates
import pygame.cursors
import pygame.mouse

HAND = ('hand.png', 12, 0)

class CursorSprite(Sprite):
    "A Sprite that follows the Cursor"

    def __init__(self, filename, x, y):
        Sprite.__init__(self)
        self.image = get_image('items', filename)
        self.rect = self.image.get_rect()
        self.pointer_x = x
        self.pointer_y = y

    def update(self):
        pos = mouse.get_pos()
        self.rect.left = pos[0] - self.pointer_x
        self.rect.top = pos[1] - self.pointer_y


class CursorWidget(Widget):
    """Mix-in widget to ensure that mouse_move is propogated to parents"""

    cursor = HAND

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self._cursor_group = RenderUpdates()
        self._loaded_cursor = None

    def draw_all(self, _surface):
        Widget.draw_all(self, _surface)
        surface = self.get_root().surface
        if self.cursor != self._loaded_cursor:
            if self.cursor is None:
                pygame.mouse.set_visible(1)
                self._cursor_group.empty()
            else:
                pygame.mouse.set_visible(0)
                self._cursor_group.empty()
                self._cursor_group.add(CursorSprite(*self.cursor))
        if self.cursor is not None:
            self._cursor_group.update()
            self._cursor_group.draw(surface)

    def mouse_delta(self, event):
        self.invalidate()

    def set_cursor(self, cursor):
        CursorWidget.cursor = cursor
