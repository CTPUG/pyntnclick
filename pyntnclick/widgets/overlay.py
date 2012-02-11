from pyntnclick.widgets.base import Button


class OverlayButton(Button):
    """A non-visiable clickable area, that causes an overlay to be
    displayed. Doesn't really understand this focus thing."""

    def __init__(self, rect, gd, image):
        self.image = image
        super(OverlayButton, self).__init__(rect, gd)

    def draw(self, surface):
        if not self.disabled:
            surface.blit(self.image, surface.get_rect())
