"""Display the game area."""

from pygame.rect import Rect
from pygame.locals import (KEYDOWN, K_LEFT, K_RIGHT, K_DOWN, K_UP, K_p,
                           K_SPACE, K_PAUSE)

from pyntnclick.constants import UP, DOWN, LEFT, RIGHT
from pyntnclick.widgets.base import Widget
from pyntnclick.engine import FlipArrowsEvent


class GameWidget(Widget):
    def __init__(self, world, offset=(0, 0)):
        self.world = world
        self.actions = self.create_action_map()
        rect = Rect(offset, world.get_size())
        super(GameWidget, self).__init__(rect)
        self.focussable = True
        self.add_callback(KEYDOWN, self.action_callback)
        self.add_callback(FlipArrowsEvent, self.flip_arrows)

    def create_action_map(self):
        actions = {}
        pause = (self.world.toggle_pause, ())
        actions[K_LEFT] = (self.world.snake.send_new_direction, (LEFT,))
        actions[K_RIGHT] = (self.world.snake.send_new_direction, (RIGHT,))
        actions[K_DOWN] = (self.world.snake.send_new_direction, (DOWN,))
        actions[K_UP] = (self.world.snake.send_new_direction, (UP,))
        actions[K_p] = pause
        actions[K_SPACE] = pause
        actions[K_PAUSE] = pause
        return actions

    def action_callback(self, ev, widget):
        if ev.key in self.actions:
            func, args = self.actions[ev.key]
            func(*args)
            return True

    def flip_arrows(self, ev, widget):
        self.world.level.flip_arrows()

    def draw(self, surface):
        self.world.update()
        self.world.draw(surface)

    def restart(self):
        self.world.restart()
        self.actions = self.create_action_map()
        self.grab_focus()
