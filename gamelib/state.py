"""Utilities and base classes for dealing with scenes."""

from albow.resource import get_image, get_sound


def initial_state():
    """Load the initial state."""
    state = State()
    # TODO: populate state
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


class Scene(object):
    """Base class for scenes."""

    FOLDER = None
    BACKGROUND = None

    def __init__(self):
        # map of thing names -> Thing objects
        self.things = {}
        self._background = get_image([self.FOLDER, self.BACKGROUND])

    def draw_background(self, surface):
        pass

    def draw_sprites(self, surface):
        pass

    def draw(self, surface):
        self.draw_background(surface)
        self.draw_sprites(surface)


class Thing(object):
    """Base class for things in a scene that you can interact with."""

    def __init__(self):
        pass

    def interact(self, item):
        pass


class Item(object):
    """Base class for inventory items."""

    def __init__(self):
        pass

