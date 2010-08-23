"""Utilities and base classes for dealing with scenes."""

from albow.resource import get_image, get_sound
from pygame.locals import BLEND_ADD


def initial_state():
    """Load the initial state."""
    state = State()
    state.load_scenes("cryo")
    #state.load_scenes("bridge")
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

    def message(self, msg):
        print msg


class Scene(object):
    """Base class for scenes."""

    # sub-folder to look for resources in
    FOLDER = None

    # name of background image resource
    BACKGROUND = None

    # name of scene (optional, defaults to folder)
    NAME = None

    # initial scene data (optional, defaults to none)
    INITIAL_DATA = None

    def __init__(self, state):
        # scene name
        self.name = self.NAME if self.NAME is not None else self.FOLDER
        # link back to state object
        self.state = state
        # map of thing names -> Thing objects
        self.things = {}
        self._background = get_image(self.FOLDER, self.BACKGROUND)
        self.data = {}
        if self.INITIAL_DATA:
            self.data.update(self.INITIAL_DATA)

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


class Thing(object):
    """Base class for things in a scene that you can interact with."""

    # sub-folder to look for resources in
    FOLDER = None

    # name of image resource
    IMAGE = None

    def __init__(self, name, rect):
        self.name = name
        # area within scene that triggers calls to interact
        self.rect = rect
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

    def interact(self, item):
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
        pass


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

