"""Mess where crew eat. Fun stuff."""

from gamelib.state import Scene, Item, Thing


class Mess(Scene):

    FOLDER = "mess"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': False,
        }


SCENES = [Mess]
