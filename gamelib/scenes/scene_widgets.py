"""Generic, game specific widgets"""

import random

from pygame import Rect
from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame.surface import Surface
from albow.resource import get_image

from gamelib.state import Thing, Result
from gamelib.constants import DEBUG
from gamelib.widgets import BoomLabel


class Interact(object):

    def __init__(self, image, rect, interact_rect):
        self.image = image
        self.rect = rect
        self.interact_rect = interact_rect

    def set_thing(self, thing):
        pass

    def draw(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.rect, None)

    def animate(self):
        return False


class InteractNoImage(Interact):

    def __init__(self, x, y, w, h):
        super(InteractNoImage, self).__init__(None, None, Rect(x, y, w, h))


class InteractText(Interact):
    """Display box with text to interact with -- mostly for debugging."""

    def __init__(self, x, y, text, bg_color=None):
        if bg_color is None:
            bg_color = (127, 127, 127)
        label = BoomLabel(text)
        label.set_margin(5)
        label.border_width = 1
        label.border_color = (0, 0, 0)
        label.bg_color = bg_color
        label.fg_color = (0, 0, 0)
        image = Surface(label.size)
        rect = Rect((x, y), label.size)
        label.draw_all(image)
        super(InteractText, self).__init__(image, rect, rect)


class InteractRectUnion(Interact):

    def __init__(self, rect_list):
        # pygame.rect.Rect.unionall should do this, but is broken
        # in some pygame versions (including 1.8, it appears)
        rect_list = [Rect(x) for x in rect_list]
        union_rect = rect_list[0]
        for rect in rect_list[1:]:
            union_rect = union_rect.union(rect)
        super(InteractRectUnion, self).__init__(None, None, union_rect)
        self.interact_rect = rect_list


class InteractImage(Interact):

    def __init__(self, x, y, image_name):
        super(InteractImage, self).__init__(None, None, None)
        self._pos = (x, y)
        self._image_name = image_name

    def set_thing(self, thing):
        self.image = get_image(thing.folder, self._image_name)
        self.rect = Rect(self._pos, self.image.get_size())
        self.interact_rect = self.rect


class InteractAnimated(Interact):
    """Interactive with an animation rather than an image"""

    # FIXME: Assumes all images are the same size
    # anim_seq - sequence of image names
    # delay - number of frames to wait between changing images

    def __init__(self, x, y, anim_seq, delay):
        self._pos = (x, y)
        self._anim_pos = 0
        self._names = anim_seq
        self._frame_count = 0
        self._anim_seq = None
        self._delay = delay

    def set_thing(self, thing):
        self._anim_seq = [get_image(thing.folder, x) for x in self._names]
        self.image = self._anim_seq[0]
        self.rect = Rect(self._pos, self.image.get_size())
        self.interact_rect = self.rect

    def animate(self):
        if self._anim_seq:
            self._frame_count += 1
            if self._frame_count > self._delay:
                self._frame_count = 0
                self._anim_pos += 1
                if self._anim_pos >= len(self._anim_seq):
                    self._anim_pos = 0
                self.image = self._anim_seq[self._anim_pos]
                # queue redraw
                return True
        return False


class GenericDescThing(Thing):
    "Thing with an InteractiveUnionRect and a description"

    INITIAL = "description"

    def __init__(self, prefix, number, description, areas):
        super(GenericDescThing, self).__init__()
        self.description = description
        self.name = '%s.%s' % (prefix, number)
        self.interacts = {
                'description' : InteractRectUnion(areas)
                }
        if DEBUG:
            # Individual colors to make debugging easier
            self._interact_hilight_color = Color(THECOLORS.keys()[number])

    def get_description(self):
        return self.description

    def is_interactive(self):
        return False


class Door(Thing):
    """A door somewhere"""

    DEST = "map"
    SCENE = None

    def __init__(self):
        self.NAME = self.SCENE + '.door'
        Thing.__init__(self)

    def is_interactive(self):
        return True

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")

    def get_description(self):
        return 'An open doorway leads to the rest of the ship.'

    def interact_default(self, item):
        return Result(random.choice([
            "Sadly, this isn't that sort of game.",
            "Your valiant efforts are foiled by the Evil Game Designer.",
            "Waving that in the doorway does nothing. Try something else, perhaps?",
            ]))

