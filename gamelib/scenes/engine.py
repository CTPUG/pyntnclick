"""Engine room where things need to be repaired."""

from gamelib.state import Scene, Item, Thing, InteractText, Result


class Engine(Scene):

    FOLDER = "engine"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Engine, self).__init__(state)
        self.add_thing(ToMap())

    def enter(self):
        return Result("Somewhere in the darkness the engine waits and bides its time.")


class ToMap(Thing):
    "Way to map."

    NAME = "engine.tomap"
    DEST = "map"

    INTERACTS = {
        "door": InteractText(100, 200, "To Map"),
        }

    INITIAL = "door"

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")


SCENES = [Engine]
