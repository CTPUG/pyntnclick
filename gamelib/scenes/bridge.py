"""Bridge where the final showdown with the AI occurs."""

from gamelib.state import Scene, Item, Thing


class Bridge(Scene):

    FOLDER = "bridge"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': False,
        }


SCENES = [Bridge]
