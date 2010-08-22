"""Utilities and base classes for dealing with scenes."""

from albow.resource import get_image, get_sound
from pygame.locals import BLEND_ADD


def initial_state():
    """Load the initial state."""
    state = State()
    state.load_scenes("cryo")
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
        # map of item name -> Item object in inventory
        self.inventory = {}
        # current scene
        self.current_scene = None

    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def load_scenes(self, modname):
        mod = __import__("gamelib.scenes.%s" % (modname,), fromlist=[modname])
        for scene_cls in mod.SCENES:
            self.add_scene(scene_cls(self))

    def set_current_scene(self, name):
        self.current_scene = self.scenes[name]

    def draw(self, surface):
        self.current_scene.draw(surface)


class Scene(object):
    """Base class for scenes."""

    # sub-folder to look for resources in
    FOLDER = None

    # name of background image resource
    BACKGROUND = None

    # name of scene (optional, defaults to folder)
    NAME = None

    def __init__(self, state):
        # scene name
        self.name = self.NAME if self.NAME is not None else self.FOLDER
        # link back to state object
        self.state = state
        # map of thing names -> Thing objects
        self.things = {}
        self._background = get_image(self.FOLDER, self.BACKGROUND)

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

    def __init__(self):
        pass

    def interact(self, item):
        pass

    def draw(self, surface):
        pass


class Item(object):
    """Base class for inventory items."""

    def __init__(self):
        pass
        # needs cursor

