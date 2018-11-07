import collections

import pygame
from pygame.locals import (MOUSEBUTTONDOWN, MOUSEBUTTONUP,
                           MOUSEMOTION, SRCALPHA, USEREVENT,
                           BLEND_RGBA_MIN)

from ..engine import UserEvent
from ..utils import convert_color


class Widget(object):

    highlight_cursor = False

    def __init__(self, pos, gd, size):
        self.pos = pos
        self.gd = gd
        self.resource = gd.resource
        self.size = size
        self.rect = pygame.Rect(pos, size if size else (0, 0))
        self.modal = False
        self.parent = None
        self.disabled = False
        self.visible = True
        self.callbacks = collections.defaultdict(list)
        # To track which widget the mouse is over
        self.mouseover_widget = self
        self.is_prepared = False

    def set_parent(self, parent):
        self.parent = parent

    def add_callback(self, eventtype, callback, *args):
        self.callbacks[eventtype].append((callback, args))

    def event(self, ev):
        "Don't override this without damn good reason"
        if self.disabled or not self.visible:
            return False

        type_ = ev.type
        if type_ == USEREVENT:
            for k in self.callbacks:
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

    def prepare(self):
        """Override me"""
        pass

    def do_prepare(self):
        if not self.is_prepared:
            self.prepare()
            self.is_prepared = True

    def disable(self):
        if not self.disabled:
            self.disabled = True
            self.prepare()
            self.is_prepared = True

    def enable(self):
        if self.disabled:
            self.disabled = False
            self.prepare()
            self.is_prepared = True

    def set_visible(self, visible):
        if self.visible != visible:
            self.visible = visible
            self.prepare()
            self.is_prepared = True

    def global_to_local(self, pos):
        x, y = pos
        return (x - self.rect.left, y - self.rect.top)


class Button(Widget):

    highlight_cursor = True

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

    def __init__(self, pos, gd, size=None):
        super(Container, self).__init__(pos, gd, size)
        self.children = []

    def event(self, ev):
        """Push an event down through the tree, and fire our own event as a
        last resort
        """
        self.mouseover_widget = self
        if ev.type in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            for child in self.children[:]:
                if child.rect.collidepoint(ev.pos):
                    result = child.event(ev)
                    self.mouseover_widget = child.mouseover_widget
                    if result:
                        return True

        else:
            # Other events go to all children first
            for child in self.children[:]:
                if child.event(ev):
                    return True
        if super(Container, self).event(ev):
            return True

    def add(self, widget):
        widget.set_parent(self)
        widget.prepare()
        self.children.append(widget)
        if not self.size:
            self.rect = self.rect.union(widget.rect)
        return widget

    def remove(self, widget):
        widget.set_parent(None)
        self.children.remove(widget)

    def remove_all(self):
        for widget in reversed(self.children[:]):
            self.remove(widget)

    def draw(self, surface):
        if self.visible:
            self.do_prepare()
            for child in self.children:
                child.draw(surface)


class ModalStackContainer(Container):

    def __init__(self, pos, gd, size, obscure_color=None):
        super(ModalStackContainer, self).__init__(pos, gd, size)
        if obscure_color is None:
            obscure_color = gd.constants.modal_obscure_color
        self.obscure_color = convert_color(obscure_color)

    @property
    def top(self):
        if self.children:
            return self.children[-1]
        return None

    def event(self, ev):
        """Only the topmost child gets events.
        """
        self.mouseover_widget = self
        if self.top:
            self.mouseover_widget = self.top.mouseover_widget
            if self.top.event(ev):
                return True

        # We skip Container's event() method and hop straight to its parent's.
        if super(Container, self).event(ev):
            return True

    def is_top(self, widget):
        return self.top is widget

    def draw(self, surface):
        if self.visible:
            self.do_prepare()
            obscure = pygame.Surface(self.rect.size, SRCALPHA)
            obscure.fill(self.obscure_color)
            for child in self.children:
                surface.blit(obscure, self.rect)
                child.draw(surface)


class Box(Container):
    """A container that draws a filled background with a border"""
    padding = 4

    def draw(self, surface):
        if self.visible:
            self.do_prepare()
            # TODO: Why isn't this done in prepare?
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


class ModalWrapper(Container):
    "A wrapper around a widget that removes itself when a mouse click occurs"

    def __init__(self, widget, close_callback=None):
        super(ModalWrapper, self).__init__(widget.rect.topleft, widget.gd,
                                           widget.rect.size)
        self.close_callback = close_callback
        self.add(widget)
        self.add_callback(MOUSEBUTTONDOWN, self.close)
        widget.add_callback(MOUSEBUTTONDOWN, self.close)

    def close(self, ev, widget):
        if self.parent:
            self.parent.remove(self)
            if self.close_callback:
                self.close_callback()
            return True


class Image(Widget):
    """Basic widget that draws an image, with an associated rect"""

    def __init__(self, pos, gd, image, size=None):
        super(Image, self).__init__(pos, gd, size)
        self.image = image
        if not size:
            self.rect.size = image.get_rect().size
        self.visible = True

    def draw(self, surface):
        self.do_prepare()
        if self.visible:
            surface.blit(self.image, self.rect)


class TranslucentImage(Image):
    """Image that can also be translucent"""

    def __init__(self, pos, gd, image, size=None):
        super(TranslucentImage, self).__init__(pos, gd, image, size)
        self.translucent = False
        surf = pygame.surface.Surface((self.rect.width, self.rect.height),
                SRCALPHA).convert_alpha()
        surf.fill(pygame.color.Color(255, 255, 255, 96))
        surf.blit(self.image, (0, 0), None, BLEND_RGBA_MIN)
        self.trans_image = surf

    def draw(self, surface):
        self.do_prepare()
        if self.visible:
            if self.translucent:
                surface.blit(self.trans_image, self.rect)
            else:
                surface.blit(self.image, self.rect)
