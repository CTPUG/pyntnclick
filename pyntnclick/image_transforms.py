"""Transforms to apply to images when they're loaded."""

from pygame.transform import rotate
from pygame.locals import BLEND_RGBA_MULT, SRCALPHA
from pygame.surface import Surface


class Transform(object):

    def __init__(self, func, *args):
        self._func = func
        self._args = args

    def __call__(self, image):
        return self._func(image, *self._args)

    def __hash__(self):
        return hash((id(self._func), self._args))

    def __eq__(self, other):
        return (self._func is other._func) and self._args == other._args

    def __repr__(self):
        return "<%s args=%r>" % (self.__class__.__name__, self._args)


# transform that does nothing
NULL = Transform(lambda x: x)

# base rotation transforms
R90 = Transform(rotate, 90)
R180 = Transform(rotate, 180)
R270 = Transform(rotate, -90)


# overlays
class Overlay(Transform):
    """Overlay another image on top of the given one."""

    def __init__(self, resources, image_name_fragments, blend=0):
        super(Overlay, self).__init__(
            self.overlay, resources, image_name_fragments, blend)

    def overlay(self, image, resources, image_name_fragments, blend):
        image = image.copy()
        overlay = resources.load_image(image_name_fragments)
        image.blit(overlay, (0, 0), None, blend)
        return image


# colour overlays
class Colour(Transform):
    """Overlay an image with a colour."""

    def __init__(self, colour, blend=BLEND_RGBA_MULT):
        super(Colour, self).__init__(self.colour, colour, blend)

    def colour(self, image, colour, blend):
        image = image.copy()
        overlay = Surface(image.get_size(), SRCALPHA, image)
        overlay.fill(colour)
        image.blit(overlay, (0, 0), None, blend)
        return image
