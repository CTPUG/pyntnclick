import pygame
from pygame.locals import SRCALPHA

from mamba.constants import FOCUS_COLOR
from mamba.data import load_image
from mamba.widgets.base import Button
from mamba.widgets.text import TextWidget


class LevelButton(Button):

    def __init__(self, rect, level, done=False):
        super(LevelButton, self).__init__(rect)
        self.level = level
        self.text = level.name
        self.done = done
        self.focussable = True
        self.border = 2
        self.rect.width = 100
        self.rect.height = 120
        self.prepare()

    def make_thumbnail(self, dest_rect):
        level_surface = pygame.Surface(self.level.get_size(), SRCALPHA)
        self.level.draw(level_surface)
        size = level_surface.get_rect().fit(dest_rect).size
        level_thumbnail = pygame.transform.scale(level_surface, size)
        return level_thumbnail

    def prepare(self):
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        self.surface.fill(0)

        dest_rect = pygame.Rect((self.border, self.border),
                                (self.rect.width - self.border,
                                 self.rect.height - self.border))
        if not hasattr(self.level, 'button_thumbnail'):
            self.level.button_thumbnail = self.make_thumbnail(dest_rect)
        self.surface.blit(self.level.button_thumbnail, dest_rect)

        if self.done:
            image = load_image('menus/tick.png')
            self.surface.blit(image, image.get_rect())

        # We only have space for two lines
        self._text_lines = self.wrap_text(self.text)[:2]

        text_height = sum(line.rect.height for line in self._text_lines)
        text_pos = self.level.button_thumbnail.get_rect().height
        text_pos += (self.rect.height - text_height - text_pos) // 2
        for line in self._text_lines:
            text_rect = pygame.Rect(((self.rect.width - line.rect.width) // 2,
                                     text_pos),
                                    line.rect.size)
            text_pos = text_rect.bottom
            self.surface.blit(line.surface, text_rect)

        color = pygame.Color(FOCUS_COLOR if self.focussed else '#444444')
        pygame.draw.rect(self.surface, color, self.surface.get_rect(),
                         self.border + 1)
        self._state = (self.done, self.focussed)

    def wrap_text(self, text):
        args = {'rect': (0, 0),
                'text': text,
                'fontsize': 12,
                'color': 'white',
               }
        w = TextWidget(**args)
        w.prepare()
        splitpoint = len(text)
        max_width = self.rect.width - (self.border * 3)
        while w.rect.width > max_width and ' ' in text[:splitpoint]:
            splitpoint = text.rfind(' ', 0, splitpoint)
            args['text'] = text[:splitpoint]
            w = TextWidget(**args)
            w.prepare()
        if splitpoint < len(text):
            return [w] + self.wrap_text(text[splitpoint + 1:])
        else:
            return [w]

    def draw(self, surface):
        if self._state != (self.done, self.focussed):
            self.prepare()
        surface.blit(self.surface, self.rect)
