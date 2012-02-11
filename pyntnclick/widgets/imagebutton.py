import pygame
from pygame.locals import SRCALPHA

from mamba.constants import COLOR, FONT_SIZE, FOCUS_COLOR
from mamba.widgets.base import Button
from mamba.widgets.text import TextWidget


class ImageButtonWidget(Button, TextWidget):
    """Text label with image on the left"""

    def __init__(self, rect, image, text, fontsize=FONT_SIZE, color=COLOR):
        self.image = image
        self.focus_color = pygame.Color(FOCUS_COLOR)
        self.padding = 5
        self.border = 3
        super(ImageButtonWidget, self).__init__(rect, text, fontsize, color)
        self.focussable = True

    def prepare(self):
        super(ImageButtonWidget, self).prepare()
        text_surface = self.surface
        # Image is already a surface
        self._focussed = self.focussed
        color = self.focus_color if self.focussed else self.color

        width = (text_surface.get_width() + self.image.get_width()
                + 5 + self.padding * 2)
        height = max(text_surface.get_height(),
                self.image.get_height()) + self.padding * 2
        self.rect.width = max(self.rect.width, width)
        self.rect.height = max(self.rect.height, height)
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.surface.fill(0)
        self.surface.blit(self.image, (self.padding, self.padding))
        self.surface.blit(text_surface,
                (self.image.get_width() + 5 + self.padding, self.padding))
        pygame.draw.rect(self.surface, color, self.surface.get_rect(),
                         self.border)

    def draw(self, surface):
        if self._focussed != self.focussed:
            self.prepare()
        super(ImageButtonWidget, self).draw(surface)
