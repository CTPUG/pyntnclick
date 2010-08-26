"""Mess where crew eat. Fun stuff."""

from random import choice

from gamelib.state import Scene, Item, CloneableItem, Thing, InteractImage, InteractNoImage, Result
from gamelib.cursor import CursorSprite


class Mess(Scene):

    FOLDER = "mess"
    BACKGROUND = "mess_hall.png"

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Mess, self).__init__(state)
        self.add_item(TubeFragments("tube_fragments"))
        self.add_item(ReplacementTubes("replacement_tubes"))
        self.add_thing(CansOnShelf())
        self.add_thing(Tubes())
        self.add_thing(ToMap())


class BaseCan(CloneableItem):
    """Base class for the cans"""

    def interact_with_full_can(self, item, state):
        return Result("You bang the cans together. It sounds like two cans being banged together.", soundfile="can_hit.ogg")

    def interact_with_dented_can(self, item, state):
        return self.interact_with_full_can(item, state)

    def interact_with_empty_can(self, item, state):
        return self.interact_with_full_can(item, state)

    def interact_with_machete(self, item, state):
        return Result("You'd mangle it beyond usefulness.")


class EmptyCan(BaseCan):
    "After emptying the full can."

    INVENTORY_IMAGE = "empty_can.png"
    CURSOR = CursorSprite('empty_can_cursor.png', 20, 30)


    def interact_with_titanium_leg(self, item, state):
        return Result("Flattening the can doesn't look like a useful thing to do")


class FullCan(BaseCan):
    "Found on the shelf."

    INVENTORY_IMAGE = "full_can.png"
    CURSOR = CursorSprite('full_can_cursor.png', 20, 30)

    def interact_with_titanium_leg(self, item, state):
        dented = DentedCan("dented_can")
        state.add_item(dented)
        state.replace_inventory_item(self, dented)
        return Result("You club the can with the femur. The can gets dented, but doesn't open.", soundfile="can_hit.ogg")


class DentedCan(BaseCan):
    "A can banged on with the femur"

    INVENTORY_IMAGE = "dented_can.png"
    CURSOR = CursorSprite('dented_can_cursor.png', 20, 30)

    def interact_with_titanium_leg(self, item, state):
        return Result("You club the can with the femur. The dents shift around, but it still doesn't open.", soundfile="can_hit.ogg")


class TubeFragments(Item):
    "Old tubes that need repair."

    INVENTORY_IMAGE = "tube_fragments.png"
    CURSOR = CursorSprite('tube_fragments_cursor.png', 36, 3)


class ReplacementTubes(Item):
    "Repaired tubes."

    INVENTORY_IMAGE = "replacement_tubes.png"
    CURSOR = CursorSprite('replacement_tubes.png', 53, 46)


class CansOnShelf(Thing):

    NAME = "mess.cans"

    INTERACTS = {
        '3cans': InteractImage(165, 209, 'shelf_3_cans.png'),
        '2cans': InteractImage(165, 209, 'shelf_2_cans.png'),
        '1cans': InteractImage(165, 209, 'shelf_1_can.png'),
        '0cans': InteractNoImage(165, 209, 50, 50),
    }

    INITIAL = '3cans'

    INITIAL_DATA = {
        'cans_available': 3,
    }

    def interact_without(self):
        starting_cans = self.get_data('cans_available')
        if starting_cans > 0:
            can = FullCan("full_can")
            self.state.add_item(can)
            self.state.add_inventory_item(can.name)
            self.set_data('cans_available', starting_cans - 1)
            self.set_interact('%icans' % (starting_cans - 1))
            return Result({
                    3: "Best before a long time in the past. Better not eat these.",
                    2: "Mmmm. Nutritious bacteria stew.",
                    1: "Candied silkworms. Who stocked this place?!",
                    }[starting_cans])
        else:
            return Result("The rest of the cans are rusted beyond usefulness.")

    def get_description(self):
        return "The contents of these cans look synthetic."


class Tubes(Thing):

    NAME = "mess.tubes"

    INTERACTS = {
        "blocked": InteractImage(250, 130, "blocking_broccoli.png"),
        "broken": InteractImage(250, 183, "broken_tubes.png"),
        "fixed": InteractImage(252, 183, "fixed_tubes.png"),
        }

    INITIAL = "blocked"


class ToMap(Thing):
    "Way to map."

    NAME = "mess.tomap"
    DEST = "map"

    INTERACTS = {
        "door": InteractNoImage(20, 390, 85, 150),
        }

    INITIAL = "door"

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")


SCENES = [Mess]
