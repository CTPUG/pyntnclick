"""Custom widgets for Suspened Sentence"""

import pygame
from pyntnclick.widgets.text import WrappedTextLabel


class JimLabel(WrappedTextLabel):
    """Custom widget for JIM's speech"""

    def __init__(self, gd, mesg):
        pos = (0, 0)
        size = None
        super(JimLabel, self).__init__(pos, gd, size=size,
                text=mesg, fontname='Monospace.ttf', fontsize=20,
                bg_color=pygame.Color(255, 175, 127, 191),
                color=pygame.Color(0, 0, 0),
                border_color=pygame.Color(127, 15, 0))

    def prepare(self):
        # Centre the widget
        super(JimLabel, self).prepare()
        self.rect.center = (self.gd.constants.screen[0] / 2,
                self.gd.constants.screen[1] / 2)
