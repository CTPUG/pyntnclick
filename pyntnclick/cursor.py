# cursor.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Sprite Cursor

from pygame.sprite import Sprite, RenderUpdates
import pygame
import pygame.color
import pygame.mouse

from .engine import Screen
from .image_transforms import Colour


class CursorSprite(Sprite):
    "A Sprite that follows the Cursor"

    def __init__(self, filename, x=None, y=None):
        Sprite.__init__(self)
        self.filename = filename
        self.pointer_x = x
        self.pointer_y = y
        self.highlighted = False
        self.highlight_colour = (255, 100, 100, 255)

    def load(self, resources):
        if not hasattr(self, 'plain_image'):
            self.highlight_transform = Colour(self.highlight_colour)
            self.plain_image = resources.get_image('items', self.filename)
            self.highlighted_image = resources.get_image(
                'items', self.filename, transforms=(self.highlight_transform,))
            self.image = self.plain_image
            self.rect = self.image.get_rect()
            if self.pointer_x is None:
                self.pointer_x = self.rect.size[0] // 2
            if self.pointer_y is None:
                self.pointer_y = self.rect.size[1] // 2

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.left = pos[0] - self.pointer_x
        self.rect.top = pos[1] - self.pointer_y

    def set_highlight(self, enable):
        self.image = self.highlighted_image if enable else self.plain_image


HAND = CursorSprite('hand.png', 12, 0)


class CursorScreen(Screen):
    """A Screen with custom cursors"""

    def setup(self):
        self._cursor_group = RenderUpdates()
        self._loaded_cursor = None
        self.set_cursor(None)

    def on_enter(self):
        super(CursorScreen, self).on_enter()
        pygame.mouse.set_visible(0)

    def on_exit(self):
        super(CursorScreen, self).on_exit()
        pygame.mouse.set_visible(1)

    def draw(self, surface):
        super(CursorScreen, self).draw(surface)
        self.set_cursor(self.game.tool)
        self._loaded_cursor.set_highlight(self.cursor_highlight())
        self._cursor_group.update()
        self._cursor_group.draw(surface)

    def set_cursor(self, item):
        if item is None or item.CURSOR is None:
            cursor = HAND
        else:
            cursor = item.CURSOR
        if cursor != self._loaded_cursor:
            self._loaded_cursor = cursor
            self._loaded_cursor.load(self.gd.resource)
            self._cursor_group.empty()
            self._cursor_group.add(self._loaded_cursor)

    def cursor_highlight(self):
        return self.container.mouseover_widget.highlight_cursor
