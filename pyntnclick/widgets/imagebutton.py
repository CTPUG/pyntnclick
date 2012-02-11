from pyntnclick.widgets.base import Button


class ImageButtonWidget(Button):
    """An image that is also a button. Whatever next?"""

    def __init__(self, rect, image):
        super(ImageButtonWidget, self).__init__(rect)
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, self.rect)
