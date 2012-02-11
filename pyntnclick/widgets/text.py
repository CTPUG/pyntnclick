import pygame
from pygame.constants import (SRCALPHA, KEYDOWN, K_ESCAPE, K_RETURN, K_UP,
        K_DOWN, K_SPACE, K_KP_ENTER)

from pyntnclick.constants import COLOR, FONT_SIZE, FOCUS_COLOR, DELETE_KEYS
from pyntnclick.widgets.base import Widget, Button
from pyntnclick.data import filepath
from pyntnclick.constants import DEFAULT_FONT


class TextWidget(Widget):
    fontcache = {}

    def __init__(self, rect, text, fontsize=FONT_SIZE, color=COLOR):
        super(TextWidget, self).__init__(rect)
        self.text = text
        self.fontsize = fontsize
        self.color = color
        self.prepare()

    def prepare(self):
        self.fontname = DEFAULT_FONT
        font = (self.fontname, self.fontsize)
        if font not in TextWidget.fontcache:
            fontfn = filepath('fonts/' + self.fontname)
            TextWidget.fontcache[font] = pygame.font.Font(fontfn,
                    self.fontsize)
        self.font = TextWidget.fontcache[font]
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
        self.focus_color = kwargs.pop('focus_color', FOCUS_COLOR)
        self.padding = kwargs.pop('padding', 10)
        self.border = kwargs.pop('border', 3)
        super(TextButton, self).__init__(*args, **kwargs)
        if not isinstance(self.focus_color, pygame.Color):
            self.focus_color = pygame.Color(self.focus_color)
        self.focussable = True

    def prepare(self):
        super(TextButton, self).prepare()
        text = self.surface
        text_rect = self.text_rect
        self._focussed = self.focussed
        if self.disabled:
            color = pygame.Color('#666666')
        elif self.focussed:
            color = self.focus_color
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
        if self._focussed != self.focussed:
            self.prepare()
        super(TextButton, self).draw(surface)

    def event(self, ev):
        if ev.type == KEYDOWN and ev.key == K_SPACE:
            return self.forced_click()
        return super(TextButton, self).event(ev)


class EntryTextWidget(TextWidget):
    def __init__(self, rect, text, **kwargs):
        self.focus_color = kwargs.pop('focus_color', FOCUS_COLOR)
        self.prompt = kwargs.pop('prompt', 'Entry:')
        self.value = text
        text = '%s %s' % (self.prompt, text)
        self.base_color = COLOR
        self.update_func = kwargs.pop('update', None)
        super(EntryTextWidget, self).__init__(rect, text, **kwargs)
        if not isinstance(self.focus_color, pygame.Color):
            self.focus_color = pygame.Color(self.focus_color)
        self.focussable = True
        self.base_color = self.color
        self.add_callback(KEYDOWN, self.update)

    def update(self, ev, widget):
        old_value = self.value
        if ev.key in DELETE_KEYS:
            if self.value:
                self.value = self.value[:-1]
        elif ev.key in (K_ESCAPE, K_RETURN, K_KP_ENTER, K_UP, K_DOWN):
            return False  # ignore these
        else:
            self.value += ev.unicode
        if old_value != self.value:
            self.text = '%s %s' % (self.prompt, self.value)
            self.prepare()
        return True

    def prepare(self):
        self.color = self.focus_color if self.focussed else self.base_color
        super(EntryTextWidget, self).prepare()
        self._focussed = self.focussed

    def draw(self, surface):
        if self._focussed != self.focussed:
            self.prepare()
        super(EntryTextWidget, self).draw(surface)
        if self.focussed:
            text_rect = self.text_rect
            # Warning, 00:30 AM code on the last Saturday
            cur_start = text_rect.move(
                    (self.rect.left + 2, self.rect.top + 3)).topright
            cur_end = text_rect.move(
                    (self.rect.left + 2, self.rect.top - 3)).bottomright
            pygame.draw.line(surface, self.focus_color,
                    cur_start, cur_end, 2)
