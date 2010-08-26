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


class EmptyCan(CloneableItem):
    "After emptying the full can."

    INVENTORY_IMAGE = "empty_can.png"
    CURSOR = CursorSprite('empty_can_cursor.png', 20, 30)

    def interact_with_full_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")

    def interact_with_dented_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")

    def interact_with_empty_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")


class FullCan(CloneableItem):
    "Found on the shelf."

    INVENTORY_IMAGE = "full_can.png"
    CURSOR = CursorSprite('full_can_cursor.png', 20, 30)

    def interact_with_titanium_leg(self, item, state):
        dented = DentedCan("dented_can")
        state.add_item(dented)
        state.replace_inventory_item(self, dented)
        return Result("You club the can with the femur. The can gets dented, but doesn't open.", soundfile="can_hit.ogg")

    def interact_with_full_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")

    def interact_with_dented_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")

    def interact_with_empty_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")


class DentedCan(CloneableItem):
    "A can banged on with the femur"

    INVENTORY_IMAGE = "dented_can.png"
    CURSOR = CursorSprite('dented_can_cursor.png', 20, 30)

    def interact_with_titanium_leg(self, item, state):
        return Result("You club the can with the femur. The dents shift around, but it still doesn't open.", soundfile="can_hit.ogg")

    def interact_with_full_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")

    def interact_with_dented_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")

    def interact_with_empty_can(self, item, state):
        return Result("You bang the cans togther. It sounds like two cans being banged togther.", soundfile="can_hit.ogg")


class TubeFragments(Item):
    "Old tubes that need repair."

    INVENTORY_IMAGE = "tube_fragments.png"
    CURSOR = CursorSprite('tube_fragments_cursor.png', 3, 60)


class ReplacementTubes(Item):
    "Repaired tubes."

    INVENTORY_IMAGE = "replacement_tubes.png"
    CURSOR = CursorSprite('replacement_tubes.png', 53, 46)


class CansOnShelf(Thing):

    NAME = "mess.cans"

    INTERACTS = {
        "cans": InteractImage(165, 209, "cans_on_shelf.png"),
        "nocans": InteractNoImage(165, 209, 50, 50),
    }

    INITIAL = "cans"

    INITIAL_DATA = {
        'cans_vended': 0,
    }

    def interact_without(self):
        starting_cans = self.get_data('cans_vended')
        if starting_cans < 3:
            can = FullCan("full_can")
            self.state.add_item(can)
            self.state.add_inventory_item(can.name)
            self.set_data('cans_vended', starting_cans + 1)
            return Result({
                    0: "Best before along time in the past. Better not eat these.",
                    1: "Mmmm. Nutritious Bacteria Stew.",
                    2: "Candied silkworms. Who stocked this place!?",
                    }[starting_cans])
        else:
            return Result("The rest of the cans are rusted beyond usefulness.")

    def get_description(self):
        return "The contents of these cans looks synthetic."


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
