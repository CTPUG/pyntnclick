import collections

import pygame
from pygame.locals import (MOUSEBUTTONDOWN, MOUSEBUTTONUP,
                           MOUSEMOTION, SRCALPHA, USEREVENT)

from pyntnclick.engine import UserEvent


class Widget(object):

    def __init__(self, rect, gd):
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(rect, (0, 0))
        self.rect = rect
        self.gd = gd
        self.resource = gd.resource
        self.modal = False
        self.parent = None
        self.disabled = False
        self.callbacks = collections.defaultdict(list)

    def add_callback(self, eventtype, callback, *args):
        self.callbacks[eventtype].append((callback, args))

    def event(self, ev):
        "Don't override this without damn good reason"
        if self.disabled:
            return True

        type_ = ev.type
        if type_ == USEREVENT:
            for k in self.callbacks.iterkeys():
                if (isinstance(k, type) and issubclass(k, UserEvent)
                        and k.matches(ev)):
                    type_ = k
                    break

        for callback, args in self.callbacks[type_]:
            if callback(ev, self, *args):
                return True
        return False

    def draw(self, surface):
        "Override me"
        pass

    def disable(self):
        if not self.disabled:
            self.disabled = True
            if hasattr(self, 'prepare'):
                self.prepare()

    def enable(self):
        if self.disabled:
            self.disabled = False
            if hasattr(self, 'prepare'):
                self.prepare()

    def global_to_local(self, pos):
        x, y = pos
        return (x - self.rect.left, y - self.rect.top)


class Button(Widget):

    def event(self, ev):
        if super(Button, self).event(ev):
            return True
        if ev.type == MOUSEBUTTONDOWN:
            for callback, args in self.callbacks['clicked']:
                if callback(ev, self, *args):
                    return True
            return False

    def forced_click(self):
        """Force calling the clicked handler"""
        for callback, args in self.callbacks['clicked']:
            if callback(None, self, *args):
                return True
        return False


class Container(Widget):

    def __init__(self, rect, gd):
        if rect is None:
            rect = pygame.Rect(0, 0, 0, 0)
        super(Container, self).__init__(rect, gd)
        self.children = []

    def event(self, ev):
        """Push an event down through the tree, and fire our own event as a
        last resort
        """
        if ev.type in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            for child in self.children[:]:
                if child.rect.collidepoint(ev.pos):
                    if child.event(ev):
                        return True

        else:
            # Other events go to all children first
            for child in self.children[:]:
                if child.event(ev):
                    return True
        if super(Container, self).event(ev):
            return True

    def add(self, widget):
        widget.parent = self
        self.children.append(widget)
        self.rect = self.rect.union(widget.rect)
        return widget

    def remove(self, widget):
        widget.parent = None
        self.children.remove(widget)

    def draw(self, surface):
        for child in self.children:
            child.draw(surface)


class GridContainer(Container):
    """Hacky container that only supports grids, won't work with Container
    children, or modal children.
    """

    def __init__(self, width, rect=None):
        super(GridContainer, self).__init__(rect)
        self.width = width

    def add(self, widget):
        assert not isinstance(widget, Container)
        assert not widget.modal
        super(GridContainer, self).add(widget)


class Box(Container):
    """A container that draws a filled background with a border"""
    padding = 4

    def draw(self, surface):
        expandrect = self.rect.move((-self.padding, -self.padding))
        expandrect.width = self.rect.width + 2 * self.padding
        expandrect.height = self.rect.height + 2 * self.padding
        border = pygame.Surface(expandrect.size, SRCALPHA)
        border.fill(pygame.Color('black'))
        surface.blit(border, expandrect)
        background = pygame.Surface(self.rect.size, SRCALPHA)
        background.fill(pygame.Color('gray'))
        surface.blit(background, self.rect)
        super(Box, self).draw(surface)


def convert_color(color):
    """Give me a pygame Color, dammit"""
    if isinstance(color, pygame.Color):
        return color
    if isinstance(color, basestring):
        return pygame.Color(color)
    return pygame.Color(*color)
