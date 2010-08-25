"""Machine room where tools and machines are found."""

from gamelib.state import Scene, Item, Thing, InteractText, Result
from gamelib.cursor import CursorSprite


class Machine(Scene):

    FOLDER = "machine"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Machine, self).__init__(state)
        self.add_thing(ToMap())
        self.add_thing(LaserWelder())
        self.add_thing(Grinder())
        self.add_item(TitaniumMachete('titanium_machete'))

    def enter(self):
        return Result("The machine room is dark and forbidding.")


class ToMap(Thing):
    "Way to map."

    NAME = "machine.tomap"
    DEST = "map"

    INTERACTS = {
        "door": InteractText(100, 200, "To Map"),
        }

    INITIAL = "door"

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")


class LaserWelder(Thing):

    NAME = "machine.laser_welder"

    INTERACTS = {
        "weld": InteractText(200, 200, "Laser welder"),
    }

    INITIAL = "weld"

    INITIAL_DATA = {
        'cans_in_place': 0,
    }

    def interact_without(self):
        if self.get_data('cans_in_place') < 1:
            return Result("The laser welder doesn't currently contain anything weldable.")
        elif self.get_data('cans_in_place') < 3:
            return Result("You'll need more cans than that.")
        else:
            self.set_data('cans_in_place', 0)
            self.state.add_inventory_item('tube_fragments')
            return Result("With high-precision spitzensparken, the cans are welded into a replacement tube.")

    def interact_with_dented_can(self, item):
        return self.interact_with_empty_can(item)

    def interact_with_empty_can(self, item):
        starting_cans = self.get_data('cans_in_place')
        if starting_cans < 3:
            self.state.remove_inventory_item(item.name)
            self.set_data('cans_in_place', starting_cans + 1)
            return Result({
                    0: "You carefully place the empty can in the area marked 'to weld'.",
                    1: "You carefully place the empty can next to the other.",
                    2: "You carefully place the empty can next to its mates.",
                    }[starting_cans])
        else:
            return Result("The machine has enough cans to weld for the moment.")

    def get_description(self):
        if self.get_data('cans_in_place') == 0:
            return "This is a Smith and Wesson 'zOMG' class high-precision laser welder."
        msg = "The laser welder looks hungry, somehow."
        if self.get_data('cans_in_place') == 1:
            msg += " It currently contains an empty can."
        elif self.get_data('cans_in_place') == 2:
            msg += " It currently contains two empty cans."
        elif self.get_data('cans_in_place') == 3:
            msg += " It currently contains three empty cans."
        return msg


class Grinder(Thing):

    NAME = "machine.grinder"

    INTERACTS = {
        "grind": InteractText(200, 300, "Grinder"),
    }

    INITIAL = "grind"

    def interact_without(self):
        return Result("It looks like it eats fingers. Perhaps a different approach is in order?")

    def interact_with_titanium_leg(self, item):
        self.state.replace_inventory_item(item, self.state.items['titanium_machete'])
        return Result("After much delicate grinding and a few close calls with"
                      " various body parts, the titanium femur now resembles"
                      " a machete more than a bone. Nice and sharp, too.")

    def get_description(self):
        return "A pretty ordinary, albeit rather industrial, grinding machine."


class TitaniumMachete(Item):
    "Titanium machete, formerly a leg."

    INVENTORY_IMAGE = "triangle.png"
    CURSOR = CursorSprite('titanium_femur_cursor.png', 47, 3)


SCENES = [Machine]
