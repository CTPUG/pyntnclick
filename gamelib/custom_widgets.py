"""Custom widgets for Suspened Sentence"""

import pygame
from pyntnclick.widgets.text import WrappedTextLabel


class JimLabel(WrappedTextLabel):
    """Custom widget for JIM's speech"""

    def __init__(self, gd, mesg):
        rect = pygame.Rect((0, 0), (1, 1))
        super(JimLabel, self).__init__(rect, gd,
                text=mesg, fontname='Monospace.ttf', fontsize=20,
                bg_color=pygame.Color(255, 175, 127, 191),
                color=pygame.Color(0, 0, 0),
                border_color=pygame.Color(127, 15, 0))
        # Centre the widget
        # Should this happen automatically in state?
        self.rect.center = (gd.constants.screen[0] / 2,
                gd.constants.screen[1] / 2)
