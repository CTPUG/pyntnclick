"""Mess where crew eat. Fun stuff."""

from gamelib.state import Scene, Item, Thing


class Mess(Scene):

    FOLDER = "mess"
    BACKGROUND = "mess_hall.png"

    INITIAL_DATA = {
        'accessible': False,
        }


SCENES = [Mess]
