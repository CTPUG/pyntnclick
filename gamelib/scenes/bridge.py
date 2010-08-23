"""Bridge where the final showdown with the AI occurs."""

from gamelib.state import Scene, Item, Thing


class Bridge(Scene):

    # FOLDER = "bridge"
    # BACKGROUND = None # TODO

    # TODO: This is for testing.
    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"
    NAME = "bridge"

    INITIAL_DATA = {
        'accessible': False,
        }


SCENES = [Bridge]
