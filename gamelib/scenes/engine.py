"""Engine room where things need to be repaired."""

from gamelib.state import Scene, Item, Thing


class Engine(Scene):

    FOLDER = "engine"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': False,
        }


SCENES = [Engine]
