"""Utilities and base classes for dealing with scenes."""

from albow.resource import get_image
from albow.utils import frame_rect
from widgets import BoomLabel
from pygame.locals import BLEND_ADD
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.color import Color

import constants
from sound import get_sound
from cursor import HAND


class Result(object):
    """Result of interacting with a thing"""

    def __init__(self, message=None, soundfile=None, detail_view=None):
        self.message = message
        self.sound = None
        if soundfile:
            self.sound = get_sound(soundfile)
        self.detail_view = detail_view

    def process(self, scene_widget):
        """Helper function to do the right thing with a result object"""
        if self.sound:
            self.sound.play()
        if self.message:
            scene_widget.show_message(self.message)
        if self.detail_view:
            scene_widget.show_detail(self.detail_view)

def initial_state(screen):
    """Load the initial state."""
    state = State(screen)
    state.load_scenes("cryo")
    state.load_scenes("bridge")
    state.load_scenes("mess")
    state.load_scenes("engine")
    state.load_scenes("machine")
    state.load_scenes("map")
    state.set_current_scene("cryo")
    state.set_do_enter_leave()
    return state


class State(object):
    """Complete game state.

    Game state consists of:

    * items
    * scenes
    """

    def __init__(self, screen):
        # map of scene name -> Scene object
        self.scenes = {}
        # map of detail view name -> DetailView object
        self.detail_views = {}
        # map of item name -> Item object
        self.items = {}
        # list of item objects in inventory
        self.inventory = []
        # currently selected tool (item)
        self.tool = None
        # current scene
        self.current_scene = None
        # current detail view
        self.current_detail = None
        # scene we came from, for enter and leave processing
        self.previous_scene = None
        # scene transion helpers
        self.do_check = None
        self.old_pos = None

        self.screen = screen

    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def add_detail_view(self, detail_view):
        self.detail_views[detail_view.name] = detail_view

    def add_item(self, item):
        self.items[item.name] = item

    def load_scenes(self, modname):
        mod = __import__("gamelib.scenes.%s" % (modname,), fromlist=[modname])
        for scene_cls in mod.SCENES:
            self.add_scene(scene_cls(self))
        if hasattr(mod, 'DETAIL_VIEWS'):
            for scene_cls in mod.DETAIL_VIEWS:
                self.add_detail_view(scene_cls(self))

    def set_current_scene(self, name):
        old_scene = self.current_scene
        self.current_scene = self.scenes[name]
        if old_scene and old_scene != self.current_scene:
            self.previous_scene = old_scene
            self.set_do_enter_leave()

    def set_current_detail(self, name):
        if name is None:
            self.current_detail = None
        else:
            self.current_detail = self.detail_views[name]
            self.current_scene._current_description = None
            self.current_scene._current_thing = None
            return self.current_detail.get_detail_size()

    def add_inventory_item(self, name):
        self.inventory.append(self.items[name])

    def remove_inventory_item(self, name):
        self.inventory.remove(self.items[name])
        # Unselect tool if it's removed
        if self.tool == self.items[name]:
            self.set_tool(None)

    def set_tool(self, item):
        self.tool = item
        if item is None:
            self.screen.set_cursor(HAND)
        else:
            self.screen.set_cursor(item.CURSOR)

    def draw(self, surface):
        if self.do_check and self.previous_scene and self.do_check == constants.LEAVE:
            # We still need to handle leave events, so still display the scene
            self.previous_scene.draw(surface)
        else:
            self.current_scene.draw(surface)

    def draw_detail(self, surface):
        self.current_detail.draw(surface)

    def interact(self, pos):
        return self.current_scene.interact(self.tool, pos)

    def interact_detail(self, pos):
        return self.current_detail.interact(self.tool, pos)

    def animate(self):
        if not self.do_check:
            return self.current_scene.animate()

    def check_enter_leave(self):
        if not self.do_check:
            return None
        if self.do_check == constants.LEAVE:
            self.do_check = constants.ENTER
            if self.previous_scene:
                return self.previous_scene.leave()
            return None
        elif self.do_check == constants.ENTER:
            self.do_check = None
            # Fix descriptions, etc.
            if self.old_pos:
                self.current_scene.mouse_move(self.tool, self.old_pos)
            return self.current_scene.enter()
        raise RuntimeError('invalid do_check value %s' % self.do_check)

    def mouse_move(self, pos):
        self.current_scene.mouse_move(self.tool, pos)
        # So we can do sensible things on enter and leave
        self.old_pos = pos

    def set_do_enter_leave(self):
        """Flag that we need to run the enter loop"""
        self.do_check = constants.LEAVE

    def mouse_move_detail(self, pos):
        self.current_detail.mouse_move(self.tool, pos)


class StatefulGizmo(object):

    # initial data (optional, defaults to none)
    INITIAL_DATA = None

    def __init__(self):
        self.data = {}
        if self.INITIAL_DATA:
            self.data.update(self.INITIAL_DATA)

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key, None)


class Scene(StatefulGizmo):
    """Base class for scenes."""

    # sub-folder to look for resources in
    FOLDER = None

    # name of background image resource
    BACKGROUND = None

    # name of scene (optional, defaults to folder)
    NAME = None

    # size (for detail views)
    SIZE = constants.SCENE_SIZE

    def __init__(self, state):
        StatefulGizmo.__init__(self)
        # scene name
        self.name = self.NAME if self.NAME is not None else self.FOLDER
        # link back to state object
        self.state = state
        # map of thing names -> Thing objects
        self.things = {}
        if self.BACKGROUND is not None:
            self._background = get_image(self.FOLDER, self.BACKGROUND)
        else:
            self._background = None
        self._current_thing = None
        self._current_description = None

    def add_item(self, item):
        self.state.add_item(item)

    def add_thing(self, thing):
        self.things[thing.name] = thing
        thing.set_scene(self)

    def remove_thing(self, thing):
        del self.things[thing.name]

    def _make_description(self, text):
        if text is None:
            return None
        label = BoomLabel(text)
        label.set_margin(5)
        label.border_width = 1
        label.border_color = (0, 0, 0)
        label.bg_color = (127, 127, 127)
        label.fg_color = (0, 0, 0)
        return label

    def draw_description(self, surface):
        if self._current_description is not None:
            sub = self.state.screen.get_root().surface.subsurface(
                Rect(5, 5, *self._current_description.size))
            self._current_description.draw_all(sub)

    def draw_background(self, surface):
        if self._background is not None:
            surface.blit(self._background, (0, 0), None)
        else:
            surface.fill((200, 200, 200))

    def draw_things(self, surface):
        for thing in self.things.itervalues():
            thing.draw(surface)

    def draw(self, surface):
        self.draw_background(surface)
        self.draw_things(surface)
        self.draw_description(surface)

    def interact(self, item, pos):
        """Interact with a particular position.

        Item may be an item in the list of items or None for the hand.

        Returns a Result object to provide feedback to the player.
        """
        for thing in self.things.itervalues():
            if thing.contains(pos):
                result = thing.interact(item)
                if result:
                    if self._current_thing:
                        # Also update descriptions if needed
                        self._current_description = self._make_description(
                                self._current_thing.get_description())
                    return result

    def animate(self):
        """Animate all the things in the scene.

           Return true if any of them need to queue a redraw"""
        result = False
        for thing in self.things.itervalues():
            if thing.animate():
                result = True
        return result

    def enter(self):
        return None

    def leave(self):
        self._current_description = None
        return None

    def mouse_move(self, item, pos):
        """Call to check whether the cursor has entered / exited a thing.

        Item may be an item in the list of items or None for the hand.
        """
        if self._current_thing is not None:
            if self._current_thing.contains(pos):
                self.state.screen.cursor_highlight(True)
                return
            else:
                self._current_thing.leave()
                self._current_thing = None
                self._current_description = None
        for thing in self.things.itervalues():
            if thing.contains(pos):
                thing.enter(item)
                self._current_thing = thing
                self._current_description = self._make_description(
                    thing.get_description())
                break
        self.state.screen.cursor_highlight(self._current_thing is not None)

    def get_detail_size(self):
        return self._background.get_size()


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


class Thing(StatefulGizmo):
    """Base class for things in a scene that you can interact with."""

    # name of thing
    NAME = None

    # sub-folder to look for resources in (defaults to scenes folder)
    FOLDER = None

    # list of Interact objects
    INTERACTS = {}

    # name first interact
    INITIAL = None

    # Interact rectangle hi-light color (for debugging)
    # (set to None to turn off)
    if constants.DEBUG:
        _interact_hilight_color = Color('red')
    else:
        _interact_hilight_color = None

    def __init__(self):
        StatefulGizmo.__init__(self)
        # name of the thing
        self.name = self.NAME
        # folder for resource (None is overridden by scene folder)
        self.folder = self.FOLDER
        # interacts
        self.interacts = self.INTERACTS
        # these are set by set_scene
        self.scene = None
        self.state = None
        self.current_interact = None
        self.rect = None
        # TODO: add masks

    def set_scene(self, scene):
        assert self.scene is None
        self.scene = scene
        if self.folder is None:
            self.folder = scene.FOLDER
        self.state = scene.state
        for interact in self.interacts.itervalues():
            interact.set_thing(self)
        self.set_interact(self.INITIAL)

    def set_interact(self, name):
        self.current_interact = self.interacts[name]
        self.rect = self.current_interact.interact_rect
        assert self.rect is not None, name

    def contains(self, pos):
        if hasattr(self.rect, 'collidepoint'):
            return self.rect.collidepoint(pos)
        else:
            # FIXME: add sanity check
            for rect in list(self.rect):
                if rect.collidepoint(pos):
                    return True
        return False

    def get_description(self):
        return None

    def is_interactive(self):
        return self.current_interact is not None

    def enter(self, item):
        """Called when the cursor enters the Thing."""
        pass

    def leave(self):
        """Called when the cursr leaves the Thing."""
        pass

    def interact(self, item):
        if not self.is_interactive():
            return
        if item is None:
            return self.interact_without()
        else:
            handler = getattr(self, 'interact_with_' + item.name, None)
            if handler is not None:
                return handler(item)
            else:
                return self.interact_default(item)

    def animate(self):
        return self.current_interact.animate()

    def interact_without(self):
        return self.interact_default(None)

    def interact_default(self, item):
        return Result("It doesn't work.")

    def draw(self, surface):
        self.current_interact.draw(surface)
        if self._interact_hilight_color is not None:
            if hasattr(self.rect, 'collidepoint'):
                frame_rect(surface, self._interact_hilight_color,
                        self.rect.inflate(1, 1), 1)
            else:
                for rect in self.rect:
                    frame_rect(surface, self._interact_hilight_color,
                            rect.inflate(1, 1), 1)


class Item(object):
    """Base class for inventory items."""

    # image for inventory
    INVENTORY_IMAGE = None

    def __init__(self, name):
        self.name = name
        self.inventory_image = get_image('items', self.INVENTORY_IMAGE)
        # TODO: needs cursor

    def get_inventory_image(self):
        return self.inventory_image

    def interact(self, tool):
        handler = getattr(self, 'interact_with_' + tool.name, None)
        inverse_handler = getattr(tool, 'interact_with_' + self.name, None)
        if handler is not None:
            return handler(tool)
        elif inverse_handler is not None:
            return inverse_handler(self)
        else:
            return self.interact_default(tool)

    def interact_default(self, tool):
        return Result("That doesn't do anything useful")

