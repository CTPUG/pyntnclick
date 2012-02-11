"""Game engine and top-level game loop."""

import pygame
import pygame.event
import pygame.display
import pygame.time
from pygame.locals import QUIT, USEREVENT


class Engine(object):
    def __init__(self, game_description):
        self._screen = None
        self._game_description = game_description
        self.screens = {}

    def set_screen(self, screen_name):
        if self._screen is not None:
            self._screen.on_exit()
        self._screen = self.screens[screen_name]
        if self._screen is not None:
            self._screen.on_enter()

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def run(self):
        """Game loop."""

        get_events = pygame.event.get
        flip = pygame.display.flip
        clock = pygame.time.Clock()
        while True:
            events = get_events()
            for ev in events:
                if ev.type == QUIT:
                    return
                elif ScreenChangeEvent.matches(ev):
                    self.set_screen(ev.screen_name)
                elif ScreenEvent.matches(ev):
                    self.screens[ev.screen_name].process_event(ev.event_name,
                                                               ev.data)
                else:
                    self._screen.dispatch(ev)
            surface = pygame.display.get_surface()
            self._screen.draw(surface)
            flip()
            self._fps = 1000.0 / clock.tick(
                    self._game_description.constants.frame_rate)


class Screen(object):
    """A top level object for the screen being displayed"""

    def __init__(self, game_description):
        # Avoid import loop
        from pyntnclick.widgets.base import Container

        self.game_description = game_description
        self.resource = game_description.resource

        self.surface_size = game_description.constants.screen
        self.surface = None
        self.container = Container(pygame.Rect((0, 0), self.surface_size))
        self.setup()

    def on_enter(self):
        """Called when this becomes the current screen."""
        # Create the surface here as flipping between editor and
        # other things kills pygame.display
        self.surface = pygame.Surface(self.surface_size)

    def on_exit(self):
        """Called when this stops being the current screen."""
        self.surface = None

    def setup(self):
        """Override for initialization"""
        pass

    def dispatch(self, ev):
        self.container.event(ev)

    def draw_background(self):
        self.surface.fill(pygame.Color('gray'))

    def draw(self, surface):
        if self.surface:
            self.draw_background()
            self.container.draw(self.surface)
            surface.blit(self.surface, self.surface.get_rect())

    def display_dialog(self, dialog):
        self.container.paused = True
        self.container.add(dialog)
        dialog.grab_focus()

    def change_screen(self, new_screen_name):
        ScreenChangeEvent.post(new_screen_name)

    def screen_event(self, screen_name, event_name, data=None):
        ScreenEvent.post(screen_name, event_name, data)

    def process_event(self, event_name, data):
        pass


class UserEvent(object):
    """A user event type allowing subclassing,
       to provide an infinate number of user-defined events
    """

    TYPE = "UNKNOWN"

    @classmethod
    def post(cls, **kws):
        ev = pygame.event.Event(USEREVENT, utype=cls.TYPE, **kws)
        pygame.event.post(ev)

    @classmethod
    def matches(cls, ev):
        return ev.type == USEREVENT and ev.utype == cls.TYPE


class ScreenChangeEvent(UserEvent):

    TYPE = "SCREEN_CHANGE"

    @classmethod
    def post(cls, screen_name):
        super(ScreenChangeEvent, cls).post(screen_name=screen_name)


class ScreenEvent(UserEvent):

    TYPE = "SCREEN_EVENT"

    @classmethod
    def post(cls, screen_name, event_name, data):
        super(ScreenEvent, cls).post(screen_name=screen_name,
                                     event_name=event_name, data=data)
