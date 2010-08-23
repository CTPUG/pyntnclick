# Button for the hand image

from albow.controls import ImageButton
from albow.resource import get_image
from albow.utils import frame_rect
from pygame.color import Color

class HandButton(ImageButton):
    """The fancy hand button for the widget"""

    sel_colour = Color('red')
    sel_width = 2

    def __init__(self, action):
        # FIXME: Yes, please.
        this_image = get_image('items', 'square.png')
        ImageButton.__init__(self, image=this_image, action=action)
        self.selected = False # Flag if we're selected

    def draw(self, surface):
        """Draw the widget"""
        ImageButton.draw(self, surface)
        if self.selected:
            rect = surface.get_rect().inflate(-self.sel_width, -self.sel_width)
            frame_rect(surface, self.sel_colour, rect, self.sel_width)

    def toggle_selected(self):
        self.selected = not self.selected

    def unselect(self):
        self.selected = False

