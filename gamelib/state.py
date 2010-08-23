"""Utilities and base classes for dealing with scenes."""

from albow.resource import get_image, get_sound
from albow.utils import frame_rect
from pygame.locals import BLEND_ADD
from pygame.rect import Rect
from pygame.color import Color

import constants


def initial_state():
    """Load the initial state."""
    state = State()
    state.load_scenes("cryo")
    state.load_scenes("bridge")
    #state.load_scenes("mess")
    #state.load_scenes("engine")
    #state.load_scenes("machine")
    #state.load_scenes("map")
    state.set_current_scene("cryo")
    return state


class State(object):
    """Complete game state.

    Game state consists of:

    * items
    * scenes
    """

    def __init__(self):
        # map of scene name -> Scene object
        self.scenes = {}
        # map of item name -> Item object
        self.items = {}
        # list of item objects in inventory
        self.inventory = []
        # Result of the most recent action
        self.msg = None
        self.description = None
        # current scene
        self.current_scene = None

    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def add_item(self, item):
        self.items[item.name] = item

    def load_scenes(self, modname):
        mod = __import__("gamelib.scenes.%s" % (modname,), fromlist=[modname])
        for scene_cls in mod.SCENES:
            self.add_scene(scene_cls(self))

    def set_current_scene(self, name):
        self.current_scene = self.scenes[name]

    def add_inventory_item(self, name):
        self.inventory.append(self.items[name])

    def remove_inventory_item(self, name):
        self.inventory.remove(self.items[name])

    def draw(self, surface):
        self.current_scene.draw(surface)

    def interact(self, item, pos):
        self.current_scene.interact(item, pos)

    def mouse_move(self, item, pos):
        self.current_scene.mouse_move(item, pos)

    def get_message(self):
        return self.msg

    def clear_message(self):
        self.msg = None

    # FIXME: sort out how state.interact and description updating should work

    def check_for_new_description(self, pos):
        """Check if the current mouse position causes a new description"""
        old_desc = self.description
        self.description = self.current_scene.check_description(pos)
        return old_desc != self.description

    def get_description(self):
        #
        # DEPRECATED
        #
        return self.description

    def message(self, msg):
        self.msg = msg


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

    def __init__(self, state):
        StatefulGizmo.__init__(self)
        # scene name
        self.name = self.NAME if self.NAME is not None else self.FOLDER
        # link back to state object
        self.state = state
        # map of thing names -> Thing objects
        self.things = {}
        self._background = get_image(self.FOLDER, self.BACKGROUND)
        self._current_thing = None

    def add_item(self, item):
        self.state.add_item(item)

    def add_thing(self, thing):
        self.things[thing.name] = thing
        thing.set_scene(self)

    def remove_thing(self, thing):
        del self.things[thing.name]

    def draw_background(self, surface):
        surface.blit(self._background, (0, 0), None, BLEND_ADD)

    def draw_things(self, surface):
        for thing in self.things.itervalues():
            thing.draw(surface)

    def draw(self, surface):
        self.draw_background(surface)
        self.draw_things(surface)

    def interact(self, item, pos):
        """Interact with a particular position.

        Item may be an item in the list of items or None for the hand.
        """
        for thing in self.things.itervalues():
            if thing.rect.collidepoint(pos):
                thing.interact(item)
                break

    def mouse_move(self, item, pos):
        """Call to check whether the cursor has entered / exited a thing.

        Item may be an item in the list of items or None for the hand.
        """
        if self._current_thing is not None:
            if self._current_thing.rect.collidepoint(pos):
                return
            else:
                self._current_thing.leave()
                self._current_thing = None
        for thing in self.things.itervalues():
            if thing.rect.collidepoint(pos):
                thing.enter(item)
                self._current_thing = thing
                break

    def check_description(self, pos):
        #
        # DEPRECATED
        #
        desc = None
        for thing in self.things.itervalues():
            # Last thing in the list that matches wins
            if Rect(thing.rect).collidepoint(pos):
                desc = thing.get_description()
        return desc


class Thing(StatefulGizmo):
    """Base class for things in a scene that you can interact with."""

    # sub-folder to look for resources in
    FOLDER = None

    # name of image resource
    IMAGE = None

    # Interact rectangle hi-light color (for debugging)
    # (set to None to turn off)
    if constants.DEBUG:
        _interact_hilight_color = Color('Red')
    else:
        _interact_hilight_color = None

    def __init__(self, name, rect):
        StatefulGizmo.__init__(self)
        self.name = name
        # area within scene to render to
        self.rect = Rect(rect)
        # area within scene that triggers calls to interact
        self.interact_rect = Rect(rect)
        # these are set by set_scene
        self.scene = None
        self.state = None
        # TODO: add masks
        # TODO: add images

    def set_scene(self, scene):
        assert self.scene is None
        self.scene = scene
        self.state = scene.state

    def message(self, msg):
        self.state.message(msg)

    def get_description(self):
        return None

    def is_interactive(self):
        return True

    def enter(self, item):
        """Called when the cursor enters the Thing."""
        print "Enter %r -> %r" % (item, self)

    def leave(self):
        """Called when the cursr leaves the Thing."""
        print "Leaves %r" % self

    def interact(self, item):
        if not self.is_interactive():
            return
        if item is None:
            self.interact_without()
        else:
            handler = getattr(self, 'interact_with_' + item.name, None)
            if handler is not None:
                handler(item)
            else:
                self.interact_default(item)

    def interact_without(self):
        self.interact_default(None)

    def interact_default(self, item):
        self.message("It doesn't work.")

    def draw(self, surface):
        if self._interact_hilight_color is not None:
            frame_rect(surface, self._interact_hilight_color,
                self.interact_rect.inflate(1, 1), 1)
        # TODO: draw image if there is one


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

