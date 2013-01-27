from pyntnclick.widgets.base import Button


class ImageButtonWidget(Button):
    """An image that is also a button. Whatever next?"""

    def __init__(self, pos, gd, image, size=None):
        super(ImageButtonWidget, self).__init__(pos, gd, size)
        if not size:
            self.rect.size = image.get_rect().size
        self.image = image
        self.visible = True

    def draw(self, surface):
        self.disabled = not self.visible
        if self.visible:
            surface.blit(self.image, self.rect)
