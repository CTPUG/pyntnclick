import pygame
from pygame.constants import SRCALPHA

from pyntnclick.widgets.base import Widget, Button


class TextWidget(Widget):
    def __init__(self, rect, gd, text, fontname=None, fontsize=None,
                 color=None):
        super(TextWidget, self).__init__(rect, gd)
        self.text = text
        constants = self.gd.constants
        if fontname is None:
            self.fontname = constants.font
        else:
            self.fontname = fontname
        if fontsize is None:
            self.fontsize = constants.font_size
        else:
            self.fontsize = fontsize
        if color is None:
            self.color = constants.text_color
        else:
            self.color = color
        self.prepare()

    def prepare(self):
        self.font = self.resource.get_font(self.fontname, self.fontsize)
        if not isinstance(self.color, pygame.Color):
            self.color = pygame.Color(self.color)
        self.surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.surface.get_rect()
        width, height = self.surface.get_rect().size
        self.rect.width = max(self.rect.width, width)
        self.rect.height = max(self.rect.height, height)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class LabelWidget(TextWidget):
    def __init__(self, rect, gd, text, fontname=None, fontsize=None,
                 color=None, bg_color=None):
        constants = gd.constants
        if bg_color is None:
            self.bg_color = constants.label_bg_color
        else:
            self.bg_color = bg_color
        super(LabelWidget, self).__init__(rect, gd, text, fontname, fontsize,
                                          color)

    def prepare(self):
        super(LabelWidget, self).prepare()
        self.rect.width += 20
        self.rect.height += 20
        new_surface = pygame.Surface(self.rect.size)
        new_surface = new_surface.convert_alpha()
        if not isinstance(self.bg_color, pygame.Color):
            self.bg_color = pygame.Color(*self.bg_color)
        new_surface.fill(self.bg_color)
        new_surface.blit(self.surface, self.surface.get_rect().move((10, 10)))
        self.surface = new_surface

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
