import collections

import pygame
from pygame.locals import (MOUSEBUTTONDOWN, MOUSEBUTTONUP,
                           MOUSEMOTION, SRCALPHA, USEREVENT)

from pyntnclick.engine import UserEvent


class Widget(object):

    def __init__(self, rect):
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(rect, (0, 0))
        self.rect = rect
        self.focussable = False
        self.focussed = False
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

    def grab_focus(self):
        if self.focussable:
            # Find the root and current focus
            root = self
            while root.parent is not None:
                root = root.parent
            focus = root
            focus_modal_base = None
            while (isinstance(focus, Container)
                    and focus.focussed_child is not None):
                if focus.modal:
                    focus_modal_base = focus
                focus = focus.children[focus.focussed_child]

            # Don't leave a modal heirarchy
            if focus_modal_base:
                widget = self
                while widget.parent is not None:
                    if widget == focus_modal_base:
                        break
                    widget = widget.parent
                else:
                    return False

            root.defocus()
            widget = self
            while widget.parent is not None:
                parent = widget.parent
                if isinstance(parent, Container):
                    idx = parent.children.index(widget)
                    parent.focussed_child = idx
                widget = parent
            self.focussed = True
            return True
        return False

    def disable(self):
        if not self.disabled:
            self.disabled = True
            self._focussable_when_enabled = self.focussable
            self.focussable = False
            if hasattr(self, 'prepare'):
                self.prepare()

    def enable(self):
        if self.disabled:
            self.disabled = False
            self.focussable = self._focussable_when_enabled
            if hasattr(self, 'prepare'):
                self.prepare()


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
        self.grab_focus()
        for callback, args in self.callbacks['clicked']:
            if callback(None, self, *args):
                return True
        return False


class Container(Widget):

    def __init__(self, rect=None):
        if rect is None:
            rect = pygame.Rect(0, 0, 0, 0)
        super(Container, self).__init__(rect)
        self.children = []
        self.focussed_child = None

    def event(self, ev):
        """Push an event down through the tree, and fire our own event as a
        last resort
        """
        if ev.type in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN):
            for child in self.children[:]:
                if child.rect.collidepoint(ev.pos):
                    if ev.type == MOUSEBUTTONDOWN and child.focussable:
                        if not child.grab_focus():
                            continue
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

    def remove(self, widget):
        widget.parent = None
        if self.focussed_child is not None:
            child = self.children[self.focussed_child]
        self.children.remove(widget)
        # We don't update the rect, for reasons of simplificty and laziness
        if self.focussed_child is not None and child in self.children:
            # Fix focus index
            self.focussed_child = self.children.index(child)
        else:
            self.focussed_child = None

    def defocus(self):
        if self.focussed_child is not None:
            child = self.children[self.focussed_child]
            if isinstance(child, Container):
                if not child.defocus():
                    return False
            child.focussed = False
            self.focussed_child = None
            return True

    def adjust_focus(self, direction):
        """Try and adjust focus in direction (integer)
        """
        if self.focussed_child is not None:
            child = self.children[self.focussed_child]
            if isinstance(child, Container):
                if child.adjust_focus(direction):
                    return True
                elif child.modal:
                    # We're modal, go back
                    if child.adjust_focus(-direction):
                        return True
            else:
                child.focussed = False

        current = self.focussed_child
        if current is None:
            current = -1 if direction > 0 else len(self.children)
        if direction > 0:
            possibles = list(enumerate(self.children))[current + 1:]
        else:
            possibles = list(enumerate(self.children))[:current]
            possibles.reverse()
        for i, child in possibles:
            if child.focussable:
                child.focussed = True
                self.focussed_child = i
                return True
            if isinstance(child, Container):
                if child.adjust_focus(direction):
                    self.focussed_child = i
                    return True
        else:
            if self.parent is None:
                if self.focussed_child is not None:
                    # At the end, mark the last one as focussed, again
                    child = self.children[self.focussed_child]
                    if isinstance(child, Container):
                        if child.adjust_focus(-direction):
                            return True
                    else:
                        child.focussed = True
                        return True
            else:
                self.focussed_child = None
            return False

    def draw(self, surface):
        if self.parent is None and not self.focussed:
            self.focussed = True
            self.adjust_focus(1)
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

    def adjust_focus(self, direction):
        if isinstance(direction, int):
            direction = (direction, 0)

        if len(self.children) == 0:
            return False

        if self.focussed_child is None:
            if sum(direction) > 0:
                self.focussed_child = 0
            else:
                self.focussed_child = len(self.children) - 1
        else:
            self.children[self.focussed_child].focussed = False
            if direction[0] != 0:
                self.focussed_child += direction[0]
            if direction[1] != 0:
                self.focussed_child += self.width * direction[1]
        if not 0 <= self.focussed_child < len(self.children):
            self.focussed_child = None
            return False
        self.children[self.focussed_child].focussed = True
        return True


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
