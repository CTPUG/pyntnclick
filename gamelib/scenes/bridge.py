"""Bridge where the final showdown with the AI occurs."""

from gamelib.state import Scene, Item, Thing, Result, InteractText


class Bridge(Scene):

    FOLDER = "bridge"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Bridge, self).__init__(state)
        self.add_thing(ToMap())

    def enter(self):
        return Result("The bridge is in a sorry, shabby state")


class ToMap(Thing):
    "Way to map."

    NAME = "bridge.tomap"
    DEST = "map"

    INTERACTS = {
        "door": InteractText(100, 200, "To Map"),
        }

    INITIAL = "door"

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")


SCENES = [Bridge]
