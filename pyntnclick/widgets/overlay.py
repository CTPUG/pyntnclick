from pyntnclick.widgets.base import Button


class OverlayButton(Button):
    """A non-visiable clickable area, that causes an overlay to be
    displayed. Doesn't really understand this focus thing."""

    def __init__(self, rect, image):
        self.image = image
        super(OverlayButton, self).__init__(rect)

    def draw(self, surface):
        if not self.disabled:
            surface.blit(self.image, surface.get_rect())
