"""Machine room where tools and machines are found."""

from gamelib.state import Scene, Item, Thing


class Machine(Scene):

    FOLDER = "machine"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': False,
        }


SCENES = [Machine]
