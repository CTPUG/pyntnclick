"""Mess where crew eat. Fun stuff."""

from gamelib.state import Scene, Item, Thing, InteractImage, InteractNoImage
from gamelib.cursor import CursorSprite


class Mess(Scene):

    FOLDER = "mess"
    BACKGROUND = "mess_hall.png"

    INITIAL_DATA = {
        'accessible': False,
        }

    def __init__(self, state):
        super(Mess, self).__init__(state)
        self.add_item(EmptyCan("empty_can"))
        self.add_item(FullCan("full_can"))
        self.add_item(TubeFragments("tube_fragments"))
        self.add_item(ReplacementTubes("replacement_tubes"))
        self.add_thing(CansOnShelf())
        self.add_thing(Tubes())


class EmptyCan(Item):
    "After emptying the full can."

    INVENTORY_IMAGE = "empty_can.png"
    CURSOR = CursorSprite('empty_can_cursor.png', 47, 3)


class FullCan(Item):
    "Found on the shelf."

    INVENTORY_IMAGE = "full_can.png"
    CURSOR = CursorSprite('full_can_cursor.png', 47, 3)


class TubeFragments(Item):
    "Old tubes that need repair."

    INVENTORY_IMAGE = "tube_fragments.png"
    CURSOR = CursorSprite('tube_fragments_cursor.png', 47, 3)


class ReplacementTubes(Item):
    "Repaired tubes."

    INVENTORY_IMAGE = "replacement_tubes.png"
    CURSOR = CursorSprite('replacement_tubes.png', 47, 3)


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
