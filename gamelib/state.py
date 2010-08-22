"""Utilities and base classes for dealing with scenes."""

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


class Scene(object):
    """Base class for scenes."""

    def __init__(self):
        pass


class Item(object):
    """Base class for items."""

    def __init__(self):
        pass

