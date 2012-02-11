import pygame
from pygame.constants import SRCALPHA

from pyntnclick.widgets.base import Widget, Button

# XXX: Needs a way to get at resource:
from pyntnclick.resources import Resources
get_font = Resources("Resources").get_font


class TextWidget(Widget):
    fontcache = {}

    def __init__(self, rect, text, fontname=None, fontsize=None, color=None):
        super(TextWidget, self).__init__(rect)
        self.text = text
        if fontname is None:
            self.fontname = 'Vera.ttf'  # FIXME: Hardcoded...
        else:
            self.fontname = fontname
        if fontsize is None:
            self.fontsize = 24  # FIXME: Hardcoded...
        else:
            self.fontsize = fontsize
        if color is None:
            self.color = 'red'  # FIXME: Hardcoded...
        else:
            self.color = color
        self.prepare()

    def prepare(self):
        self.font = get_font(self.fontname, self.fontsize)
        if not isinstance(self.color, pygame.Color):
            self.color = pygame.Color(self.color)
        self.surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.surface.get_rect()
        width, height = self.surface.get_rect().size
        self.rect.width = max(self.rect.width, width)
        self.rect.height = max(self.rect.height, height)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class TextButton(Button, TextWidget):
    def __init__(self, *args, **kwargs):
        self.padding = kwargs.pop('padding', 10)
        self.border = kwargs.pop('border', 3)
        super(TextButton, self).__init__(*args, **kwargs)

    def prepare(self):
        super(TextButton, self).prepare()
        text = self.surface
        text_rect = self.text_rect
        if self.disabled:
            color = pygame.Color('#666666')
        else:
            color = self.color

        width = text_rect.width + self.padding * 2
        height = text_rect.height + self.padding * 2
        self.rect.width = max(self.rect.width, width)
        self.rect.height = max(self.rect.height, height)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.surface.fill(0)
        self.surface.blit(text, text.get_rect().move(self.padding,
                                                     self.padding))
        pygame.draw.rect(self.surface, color, self.surface.get_rect(),
                         self.border)

    def draw(self, surface):
        super(TextButton, self).draw(surface)
