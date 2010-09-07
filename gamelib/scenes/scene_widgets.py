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


class InteractImageRect(InteractImage):
    def __init__(self, x, y, image_name, r_x, r_y, r_w, r_h):
        super(InteractImageRect, self).__init__(x, y, image_name)
        self._r_pos = (r_x, r_y)
        self._r_size = (r_w, r_h)

    def set_thing(self, thing):
        super(InteractImageRect, self).set_thing(thing)
        self.interact_rect = Rect(self._r_pos, self._r_size)


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

    def is_interactive(self, tool=None):
        return False


class Door(Thing):
    """A door somewhere"""

    DEST = "map"
    SCENE = None

    def __init__(self):
        self.NAME = self.SCENE + '.door'
        Thing.__init__(self)

    def is_interactive(self, tool=None):
        return True

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")

    def get_description(self):
        return 'An open doorway leads to the rest of the ship.'

    def interact_default(self, item):
        return self.interact_without()


def make_jim_dialog(mesg, state):
    "Utility helper function"
    if state.scenes['bridge'].get_data('ai status') == 'online':
        return Result(mesg, style='JIM')
    else:
        return None


class BaseCamera(Thing):
    "Base class for the camera puzzles"

    INITIAL = 'online'
    INITIAL_DATA = {
         'state': 'online',
    }

    def get_description(self):
        status = self.state.scenes['bridge'].get_data('ai status')
        if status == 'online':
            return "A security camera watches over the room"
        elif status == 'looping':
            return "The security camera is currently offline but should be working soon"
        else:
            return "The security camera is powered down"

    def is_interactive(self, tool=None):
        return self.state.scenes['bridge'].get_data('ai status') == 'online'

    def interact_with_escher_poster(self, item):
        # Order matters here, because of helper function
        if self.state.scenes['bridge'].get_data('ai status') == 'online':
            ai_response = make_jim_dialog("3D scene reconstruction failed. Critical error. Entering emergency shutdown.", self.state)
            self.state.scenes['bridge'].set_data('ai status', 'looping')
            return ai_response

    def animate(self):
        ai_status = self.state.scenes['bridge'].get_data('ai status')
        if ai_status != self.get_data('status'):
            self.set_data('status', ai_status)
            self.set_interact(ai_status)
        super(BaseCamera, self).animate()

