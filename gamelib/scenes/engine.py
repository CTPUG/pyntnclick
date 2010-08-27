"""Engine room where things need to be repaired."""

from gamelib.state import Scene, Item, Thing, InteractText, Result
from gamelib.scenes.scene_widgets import Door


class Engine(Scene):

    FOLDER = "engine"
    BACKGROUND = "engine_room.png"

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Engine, self).__init__(state)
        self.add_thing(ToMap())

    def enter(self):
        return Result("Somewhere in the darkness the engine waits and bides its time.")


class ToMap(Door):

    NAME = "engine.tomap"

    INTERACTS = {
        "door": InteractText(100, 200, "To Map"),
        }

    INITIAL = "door"


SCENES = [Engine]
