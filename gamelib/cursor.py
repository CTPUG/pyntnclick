# cursor.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Sprite Cursor

from albow.screen import Screen
from albow.widget import Widget
from albow.resource import get_image
import pygame.mouse as mouse
from pygame.sprite import Sprite, RenderUpdates
import pygame.cursors
import pygame.mouse

# FIXME: make this a all transparent cursor
BLANK_CURSOR=pygame.cursors.broken_x

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

    def mouse_move(self, event):
        self.call_parent_handler('mouse_move', event)

    def get_cursor(self, event):
        return BLANK_CURSOR


class CursorSpriteScreen(Screen):
    "A Screen with a CursorSprite"

    def __init__(self, shell):
        Screen.__init__(self, shell)

        sprite = CursorSprite('hand')
        self.cursor_group = RenderUpdates(sprite)

    def draw(self, surface):
        if self.get_cursor(None) == pygame.mouse.get_cursor():
            self.cursor_group.update()
            self.cursor_group.draw(surface)

    def mouse_move(self, event):
        self.invalidate()

    def get_cursor(self, event):
        return BLANK_CURSOR
