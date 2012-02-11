import pygame

from pyntnclick.widgets.base import Button


class ImageButtonWidget(Button):
    """An image that is also a button. Whatever next?"""

    def __init__(self, rect, image):
        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(rect, image.get_size())
        super(ImageButtonWidget, self).__init__(rect)
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, self.rect)
