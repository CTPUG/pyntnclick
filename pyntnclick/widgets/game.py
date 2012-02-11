"""Display the game area."""

from pygame.rect import Rect

from pyntnclick.widgets.base import Widget
from pyntnclick.engine import FlipArrowsEvent


class GameWidget(Widget):
    def __init__(self, world, offset=(0, 0)):
        self.world = world
        rect = Rect(offset, world.get_size())
        super(GameWidget, self).__init__(rect)
        self.focussable = True
        self.add_callback(FlipArrowsEvent, self.flip_arrows)

    def flip_arrows(self, ev, widget):
        self.world.level.flip_arrows()

    def draw(self, surface):
        self.world.update()
        self.world.draw(surface)

    def restart(self):
        self.world.restart()
        self.grab_focus()
