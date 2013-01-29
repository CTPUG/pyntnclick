"""Interactive elements within a Scene."""


from pygame import Rect
from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame.surface import Surface

from pyntnclick.state import Thing
from pyntnclick.utils import convert_color, render_text
from pyntnclick.widgets.text import LabelWidget


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


class InteractDebugText(Interact):
    """Display box with text to interact with -- mostly for debugging."""

    def __init__(self, x, y, text, bg_color=None):
        if bg_color is None:
            bg_color = (127, 127, 127)
        label = LabelWidget((0, 0), text)
        # label.set_margin(5)
        # label.border_width = 1
        # label.border_color = (0, 0, 0)
        # label.bg_color = bg_color
        # label.fg_color = (0, 0, 0)
        image = Surface(label.size)
        rect = Rect((x, y), label.size)
        label.draw_all(image)
        super(InteractDebugText, self).__init__(image, rect, rect)


class InteractText(Interact):
    """Display a text string on a transparent background.

       Used so we can easily include translatable strings in the scenes"""

    def __init__(self, x, y, w, h, text, color, max_font_size, font=None,
            centre=True):
        self._text = text
        self._color = convert_color(color)
        self._max_font_size = max_font_size
        self._font = font
        self._centre = centre
        rect = Rect((x, y), (w, h))
        super(InteractText, self).__init__(None, rect, rect)

    def set_thing(self, thing):
        font_size = self._max_font_size
        if not self._font:
            # Pull the default font out of constants
            self._font = thing.gd.constants.font
        bg_color = Color(0, 0, 0, 0)  # transparent background
        self.image = render_text(self._text, self._font, font_size,
                self._color, bg_color, thing.resource, self.rect.size,
                self._centre)


class InteractRectUnion(Interact):

    def __init__(self, rect_list):
        super(InteractRectUnion, self).__init__(None, None, None)
        rect_list = [Rect(x) for x in rect_list]
        self.interact_rect = rect_list


class InteractUnion(Interact):
    """An interact made out of other interacts"""

    def __init__(self, interact_list):
        super(InteractUnion, self).__init__(None, None, None)
        self._interact_list = interact_list

    def set_thing(self, thing):
        interact_list = []
        for sub_interact in self._interact_list:
            sub_interact.set_thing(thing)
            sub_rect = sub_interact.interact_rect
            if hasattr(sub_rect, 'collidepoint'):
                interact_list.append(sub_interact.interact_rect)
            else:
                interact_list.extend(sub_interact.interact_rect)
        self.interact_rect = interact_list

    def draw(self, surface):
        for sub_interact in self._interact_list:
            sub_interact.draw(surface)

    def animate(self):
        for sub_interact in self._interact_list:
            sub_interact.animate()


class InteractImage(Interact):

    def __init__(self, x, y, image_name):
        super(InteractImage, self).__init__(None, None, None)
        self._pos = (x, y)
        self._image_name = image_name

    def set_thing(self, thing):
        self.image = thing.resource.get_image(thing.folder, self._image_name)
        self.rect = Rect(self._pos, self.image.get_size())
        self.interact_rect = self.rect

    def __repr__(self):
        return '<InteractImage: %s>' % self._image_name


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
        self._anim_seq = [thing.resource.get_image(thing.folder, x)
                          for x in self._names]
        self.image = self._anim_seq[0]
        self.rect = Rect(self._pos, self.image.get_size())
        for image in self._anim_seq:
            assert image.get_size() == self.rect.size
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


class TakeableThing(Thing):
    "Thing that can be taken."

    INITIAL_DATA = {
        'taken': False,
    }

    ITEM = None

    def __init__(self):
        # In case a subclass replaces INITIAL_DATA and breaks 'taken'.
        assert self.INITIAL_DATA['taken'] in (True, False)
        super(TakeableThing, self).__init__()

    def should_add(self):
        return not self.get_data('taken')

    def take(self):
        self.set_data('taken', True)
        self.game.add_inventory_item(self.ITEM)
        self.scene.remove_thing(self)


class GenericDescThing(Thing):
    "Thing with an InteractiveUnionRect and a description"

    INITIAL = "description"

    def __init__(self, prefix, number, description, areas):
        super(GenericDescThing, self).__init__()
        self.description = description
        self.name = '%s.%s' % (prefix, number)
        self.interacts = {
                'description': InteractRectUnion(areas)
                }
        # Individual colors to make debugging easier
        self._interact_hilight_color = Color(THECOLORS.keys()[number])

    def get_description(self):
        return self.description

    def is_interactive(self, tool=None):
        return False
