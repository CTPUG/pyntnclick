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

    def set_screen(self, screen):
        if self._screen is not None:
            self._screen.on_exit()
        self._screen = screen
        if self._screen is not None:
            self._screen.on_enter()

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
                    self.set_habitat(ev.habitat)
                else:
                    self._screen.dispatch(ev)
            surface = pygame.display.get_surface()
            self._habitat.draw(surface)
            flip()
            self._fps = 1000.0 / clock.tick(
                    self.game_description.constants.fps)


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
    def post(cls, screen):
        super(ScreenChangeEvent, cls).post(screen=screen)
