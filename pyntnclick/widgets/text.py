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
    def __init__(self, rect, gd, *args, **kwargs):
        constants = gd.constants
        self.padding = kwargs.pop('padding', constants.label_padding)
        self.border = kwargs.pop('border', constants.label_border)
        self.bg_color = kwargs.pop('bg_color', constants.label_bg_color)
        if not isinstance(self.bg_color, pygame.Color):
            self.bg_color = pygame.Color(*self.bg_color)
        self.border_color = kwargs.pop('border_color',
                                       constants.label_border_color)
        if not isinstance(self.border_color, pygame.Color):
            self.border_color = pygame.Color(*self.border_color)
        super(LabelWidget, self).__init__(rect, gd, *args, **kwargs)

    def prepare(self):
        super(LabelWidget, self).prepare()
        self.rect.width += 2 * self.padding
        self.rect.height += 2 * self.padding
        new_surface = pygame.Surface(self.rect.size)
        new_surface = new_surface.convert_alpha()
        new_surface.fill(self.bg_color)
        new_surface.blit(self.surface, self.surface.get_rect().move(
                (self.padding, self.padding)))
        if self.border:
            pygame.draw.rect(new_surface, self.border_color,
                             new_surface.get_rect(),
                             self.border)
        self.surface = new_surface

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class TextButton(Button, TextWidget):
    def __init__(self, rect, gd, *args, **kwargs):
        constants = gd.constants
        self.padding = kwargs.pop('padding', constants.label_padding)
        self.border = kwargs.pop('border', constants.label_border)
        self.disabled_color = kwargs.pop('disabled_color',
                                         constants.disabled_color)
        if not isinstance(self.disabled_color, pygame.Color):
            self.disabled_color = pygame.Color(*self.disabled_color)
        super(TextButton, self).__init__(rect, gd, *args, **kwargs)

    def prepare(self):
        super(TextButton, self).prepare()
        text = self.surface
        text_rect = self.text_rect
        color = self.disabled_color if self.disabled else self.color

        width = text_rect.width + self.padding * 2
        height = text_rect.height + self.padding * 2
        self.rect.width = max(self.rect.width, width)
        self.rect.height = max(self.rect.height, height)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.surface.fill(0)
        offset = (
            (self.rect.width - width) / 2 + self.padding,
            (self.rect.height - height) / 2 + self.padding)
        self.surface.blit(text, text.get_rect().move(offset))
        if self.border:
            pygame.draw.rect(self.surface, color, self.surface.get_rect(),
                             self.border)

    def draw(self, surface):
        super(TextButton, self).draw(surface)
