"""Mess where crew eat. Fun stuff."""

from gamelib.state import Scene, Item, Thing, InteractImage, InteractNoImage


class Mess(Scene):

    FOLDER = "mess"
    BACKGROUND = "mess_hall.png"

    INITIAL_DATA = {
        'accessible': False,
        }

    def __init__(self, state):
        super(Mess, self).__init__(state)
        self.add_thing(CansOnShelf())
        self.add_thing(Tubes())


class CansOnShelf(Thing):

    NAME = "mess.cans"

    INTERACTS = {
        "cans": InteractImage(165, 209, "cans_on_shelf.png"),
        "nocans": InteractNoImage(165, 209, 50, 50),
    }

    INITIAL = "cans"


class Tubes(Thing):

    NAME = "mess.tubes"

    INTERACTS = {
        "blocked": InteractImage(250, 130, "blocking_broccoli.png"),
        "broken": InteractImage(250, 183, "broken_tubes.png"),
        "fixed": InteractImage(252, 183, "fixed_tubes.png"),
        }

    INITIAL = "blocked"


SCENES = [Mess]
