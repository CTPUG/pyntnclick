# cursor.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Sprite Cursor

from albow.resource import get_image
from albow.widget import Widget
from pygame.sprite import Sprite, RenderUpdates
from pygame.rect import Rect
import pygame
import pygame.color
import pygame.cursors
import pygame.mouse

# XXX: Need a way to get at the constants
from pyntnclick.constants import GameConstants
SCENE_SIZE = GameConstants().scene_size


class CursorSprite(Sprite):
    "A Sprite that follows the Cursor"

    def __init__(self, filename, x=None, y=None):
        Sprite.__init__(self)
        self.filename = filename
        self.pointer_x = x
        self.pointer_y = y
        self.highlighted = False

    def load(self):
        if not hasattr(self, 'plain_image'):
            self.plain_image = get_image('items', self.filename)
            self.image = self.plain_image
            self.rect = self.image.get_rect()

            if self.pointer_x is None:
                self.pointer_x = self.rect.size[0] // 2
            if self.pointer_y is None:
                self.pointer_y = self.rect.size[1] // 2

            self.highlight = pygame.Surface(self.rect.size)
            color = pygame.color.Color(255, 100, 100, 0)
            self.highlight.fill(color)

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.left = pos[0] - self.pointer_x
        self.rect.top = pos[1] - self.pointer_y

    def set_highlight(self, enable):
        if enable != self.highlighted:
            self.load()
            self.highlighted = enable
            self.image = self.plain_image.copy()
            if enable:
                self.image.blit(self.highlight, self.highlight.get_rect(),
                                None, pygame.BLEND_MULT)


HAND = CursorSprite('hand.png', 12, 0)


class CursorWidget(Widget):
    """Mix-in widget to ensure that mouse_move is propogated to parents"""

    cursor = HAND
    _cursor_group = RenderUpdates()
    _loaded_cursor = None

    def __init__(self, screen, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.screen = screen

    def enter_screen(self):
        pygame.mouse.set_visible(0)

    def leave_screen(self):
        pygame.mouse.set_visible(1)

    def draw_all(self, surface):
        Widget.draw_all(self, surface)
        self.draw_cursor(self.get_root().surface)

    def draw_cursor(self, surface):
        self.set_cursor(self.screen.state.tool)
        self.cursor.set_highlight(self.cursor_highlight())
        if self.cursor is not None:
            self._cursor_group.update()
            self._cursor_group.draw(surface)

    def mouse_delta(self, event):
        self.invalidate()

    @classmethod
    def set_cursor(cls, item):
        if item is None or item.CURSOR is None:
            cls.cursor = HAND
        else:
            cls.cursor = item.CURSOR
        if cls.cursor != cls._loaded_cursor:
            cls._loaded_cursor = cls.cursor
            if cls.cursor is None:
                pygame.mouse.set_visible(1)
                cls._cursor_group.empty()
            else:
                pygame.mouse.set_visible(0)
                cls.cursor.load()
                cls._cursor_group.empty()
                cls._cursor_group.add(cls.cursor)

    def cursor_highlight(self):
        if not Rect((0, 0), SCENE_SIZE).collidepoint(pygame.mouse.get_pos()):
            return False
        if self.screen.state.highlight_override:
            return True
        current_thing = self.screen.state.current_thing
        if current_thing:
            return current_thing.is_interactive()
        return False
