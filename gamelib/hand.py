# Button for the hand image

from constants import BUTTON_SIZE

from albow.controls import ImageButton
from albow.resource import get_image
from albow.utils import frame_rect
from pygame.color import Color
from pygame.rect import Rect


class HandButton(ImageButton):
    """The fancy hand button for the widget"""

    def __init__(self, action):
        # FIXME: Yes, please.
        this_image = get_image('items', 'hand.png')
        ImageButton.__init__(self, image=this_image, action=action)
        self.set_rect(Rect(0, 0, BUTTON_SIZE, BUTTON_SIZE))

