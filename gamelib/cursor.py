# cursor.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Sprite Cursor

from albow.widget import Widget
from albow.resource import get_image
import pygame.mouse as mouse
from pygame.sprite import Sprite, RenderUpdates
import pygame.cursors
import pygame.mouse


class CursorSprite(Sprite):
    "A Sprite that follows the Cursor"

    def __init__(self, filename):
        Sprite.__init__(self)
        self.image = get_image('items', filename + '.png')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.midtop = mouse.get_pos()


class CursorWidget(Widget):
    """Mix-in widget to ensure that mouse_move is propogated to parents"""

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self._cursor_group = RenderUpdates()
        self._cursor_name = ''

    def draw_all(self, _surface):
        Widget.draw_all(self, _surface)
        surface = self.get_root().surface
        cursor = self.get_sprite_cursor()
        if cursor != self._cursor_name:
            if self.get_sprite_cursor() is None:
                pygame.mouse.set_visible(1)
                self._cursor_group.empty()
            else:
                pygame.mouse.set_visible(0)
                self._cursor_group.empty()
                self._cursor_group.add(CursorSprite(cursor))
        if cursor is not None:
            self._cursor_group.update()
            self._cursor_group.draw(surface)

    def mouse_delta(self, event):
        self.invalidate()

    def get_sprite_cursor(self):
        return 'hand'
