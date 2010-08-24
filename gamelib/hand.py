# Button for the hand image

from constants import BUTTON_SIZE

from albow.controls import Image
from albow.resource import get_image
from pygame.rect import Rect


class HandButton(Image):
    """The fancy hand button for the widget"""

    def __init__(self, action):
        # FIXME: Yes, please.
        this_image = get_image('items', 'hand.png')
        Image.__init__(self, image=this_image)
        self.action = action
        self.set_rect(Rect(0, 0, BUTTON_SIZE, BUTTON_SIZE))

    def mouse_down(self, event):
        self.action()

