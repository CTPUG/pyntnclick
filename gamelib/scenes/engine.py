"""Engine room where things need to be repaired."""

from gamelib.state import Scene, Item, Thing, Result
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractAnimated, GenericDescThing)


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

    SCENE = "engine"

    INTERACTS = {
        "door": InteractNoImage(663, 360, 108, 193),
        }

    INITIAL = "door"


SCENES = [Engine]
