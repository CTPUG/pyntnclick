"""Machine room where tools and machines are found."""

from pyntnclick.state import Scene, Item, Thing, Result
from pyntnclick.cursor import CursorSprite
from pyntnclick.scenewidgets import (
    InteractNoImage, InteractImage, InteractAnimated, GenericDescThing,
    TakeableThing)

from gamelib.scenes.game_widgets import Door


class Machine(Scene):

    FOLDER = "machine"
    BACKGROUND = "machine_room.png"

    def setup(self):
        self.add_thing(ToMap())
        self.add_thing(LaserWelderSlot())
        self.add_thing(LaserWelderButton())
        self.add_thing(LaserWelderPowerLights())
        self.add_thing(Grinder())
        self.add_thing(ManualThing())
        self.add_item(TitaniumMachete('machete'))
        self.add_item(CryoPipesOne('cryo_pipes_one'))
        self.add_item(CryoPipesTwo('cryo_pipes_two'))
        self.add_item(CryoPipesThree('cryo_pipes_three'))
        self.add_item(Manual('manual'))
        self.add_thing(GenericDescThing('machine.wires', 2,
            "Wires run to all the machines in the room",
            (
                (250, 172, 252, 12),
                (388, 183, 114, 13),
                (496, 112, 36, 64),
                (533, 85, 19, 45),
                (647, 114, 10, 308),
                (111, 96, 13, 285),
                (152, 106, 34, 30),
                (189, 136, 27, 28),
                (222, 157, 24, 25),
                (120, 86, 34, 29),
                (110, 80, 21, 15),
                (383, 196, 12, 56),
                (553, 61, 26, 50),
                (574, 39, 16, 48),
                (648, 85, 22, 26),
                (674, 54, 23, 36),
                )))
        self.add_thing(GenericDescThing('machine.diagram', 3,
            "A wiring diagram of some sort",
            ((694, 140, 94, 185),)))
        self.add_thing(GenericDescThing('machine.powerpoint', 4,
            "The cables to this power point have been cut",
            ((155, 22, 92, 74),)))
        self.add_thing(GenericDescThing("machine.powerpoint", 5,
            "All the machines run off this powerpoint",
            ((593, 19, 74, 57),)))
        self.add_thing(GenericDescThing("machine.drill_press", 6,
            "An impressive looking laser drill press",
            (
                (519, 338, 36, 63),
                (545, 348, 93, 46),
                (599, 309, 41, 150),
                (588, 445, 66, 42),
                (616, 479, 41, 14),
                (527, 393, 15, 17),
                (510, 360, 13, 11),
                (532, 331, 14, 11),
                (605, 304, 26, 8),
            )))
        self.add_thing(GenericDescThing("machine.drill_press_block", 7,
            "The block for the laser drill press",
            ((461, 446, 38, 27),)))


class ToMap(Door):

    SCENE = "machine"

    INTERACTS = {
        "door": InteractNoImage(695, 350, 97, 212),
        }

    INITIAL = "door"


class LaserWelderSlot(Thing):

    NAME = "machine.welder.slot"

    INTERACTS = {
        "empty": InteractImage(241, 310, "welder_empty.png"),
        "can": InteractImage(241, 310, "welder_can.png"),
        "tube": InteractImage(241, 310, "welder_pipe.png"),
        "can_and_tube": InteractImage(241, 310, "welder_can_pipe.png"),
    }

    INITIAL = "empty"

    INITIAL_DATA = {
        'contents': set(),
    }

    def select_interact(self):
        contents = self.get_data('contents')
        if not contents:
            return "empty"
        elif len(contents) == 1:
            if "can" in contents:
                return "can"
            elif "tube" in contents:
                return "tube"
        else:
            return "can_and_tube"

    def interact_without(self):
        return Result("You really don't want to put your hand in there.")

    def interact_with_empty_can(self, item):
        contents = self.get_data('contents')
        if "can" in contents:
            return Result("There is already a can in the welder.")
        self.game.remove_inventory_item(item.name)
        contents.add("can")
        self.set_interact()
        return Result("You carefully place the can in the laser welder.")

    def interact_with_tube_fragment(self, item):
        contents = self.get_data('contents')
        if "tube" in contents:
            return Result("There is already a tube fragment in the welder.")
        self.game.remove_inventory_item(item.name)
        contents.add("tube")
        self.set_interact()
        return Result("You carefully place the tube fragments in the"
                      " laser welder.")

    def get_description(self):
        contents = self.get_data('contents')
        if not contents:
            return ("This is a Smith and Wesson 'zOMG' class high-precision"
                    " laser welder.")
        if len(contents) == 1:
            msg = "The laser welder looks hungry, somehow."
            if "can" in contents:
                msg += " It currently contains an empty can."
            elif "tube" in contents:
                msg += " It currently contains a tube fragment."
        elif len(contents) == 2:
            msg = "The laser welder looks expectant. "
            if "can" in contents and "tube" in contents:
                msg += (" It currently contains an empty can and a"
                        " tube fragment.")
        return msg


class LaserWelderButton(Thing):

    NAME = "machine.welder.button"

    INTERACTS = {
        "button": InteractNoImage(406, 389, 28, 31),
    }

    INITIAL = "button"

    def interact_without(self):
        welder_slot = self.scene.things["machine.welder.slot"]
        contents = welder_slot.get_data("contents")
        if not contents:
            return Result("The laser welder doesn't currently contain"
                          " anything weldable.")
        elif len(contents) == 1:
            if "can" in contents:
                return Result("The laser welder needs something to weld the"
                              " can to.")
            elif "tube" in contents:
                return Result("The laser welder needs something to weld the"
                              " tube fragments to.")
        else:
            welder_slot.set_data("contents", set())
            welder_slot.set_interact()
            if self.game.is_in_inventory("cryo_pipes_one"):
                self.game.replace_inventory_item("cryo_pipes_one",
                                                  "cryo_pipes_two")
                return Result("With high-precision spitzensparken, you weld"
                              " together a second pipe. You bundle the two"
                              " pipes together.",
                        soundfile='laser.ogg')
            elif self.game.is_in_inventory("cryo_pipes_two"):
                self.game.replace_inventory_item("cryo_pipes_two",
                                                  "cryo_pipes_three")
                return Result("With high-precision spitzensparken, you create"
                              " yet another pipe. You store it with the other"
                              " two.",
                        soundfile='laser.ogg')
            elif self.game.is_in_inventory("cryo_pipes_three"):
                # just for safety
                return None
            else:
                self.game.add_inventory_item("cryo_pipes_one")
                return Result("With high-precision spitzensparken, the can and"
                              " tube are welded into a whole greater than the"
                              " sum of the parts.",
                        soundfile='laser.ogg')


class LaserWelderPowerLights(Thing):

    NAME = "machine.welder.lights"

    INTERACTS = {
        "lights": InteractAnimated(199, 273, ["power_lights_%d.png" % i for i
                                              in range(8) + range(6, 0, -1)],
                                   10),
    }

    INITIAL = 'lights'

    def get_description(self):
        return "The power lights pulse expectantly."


class CryoPipesOne(Item):
    "A single cryo pipe (made from a tube fragment and can)."

    INVENTORY_IMAGE = "cryo_pipes_one.png"
    CURSOR = CursorSprite('cryo_pipes_one_cursor.png')
    TOOL_NAME = "cryo_pipes_one"


class CryoPipesTwo(Item):
    "Two cryo pipes (each made from a tube fragment and can)."

    INVENTORY_IMAGE = "cryo_pipes_two.png"
    CURSOR = CursorSprite('cryo_pipes_two_cursor.png')
    TOOL_NAME = "cryo_pipes_two"


class CryoPipesThree(Item):
    "Three cryo pipes (each made from a tube fragment and can)."

    INVENTORY_IMAGE = "cryo_pipes_three.png"
    CURSOR = CursorSprite('cryo_pipes_three_cursor.png')
    TOOL_NAME = "cryo_pipes_three"


class Grinder(Thing):

    NAME = "machine.grinder"

    INTERACTS = {
        "grind": InteractNoImage(86, 402, 94, 63),
    }

    INITIAL = "grind"

    def interact_without(self):
        return Result("It looks like it eats fingers. Perhaps a different"
                      " approach is in order?")

    def interact_with_titanium_leg(self, item):
        self.game.replace_inventory_item(item.name, 'machete')
        return Result("After much delicate grinding and a few close calls with"
                      " various body parts, the titanium femur now resembles"
                      " a machete more than a bone. Nice and sharp, too.",
                      soundfile="grinder.ogg")

    def get_description(self):
        return "A pretty ordinary, albeit rather industrial, grinding machine."


class TitaniumMachete(Item):
    "Titanium machete, formerly a leg."

    INVENTORY_IMAGE = "machete.png"
    CURSOR = CursorSprite('machete_cursor.png', 23, 1)


class ManualThing(TakeableThing):

    NAME = "machine.manual"

    INTERACTS = {
        "manual": InteractImage(432, 493, "manual_on_floor.png"),
    }

    INITIAL = "manual"
    ITEM = 'manual'

    def interact_without(self):
        self.take()
        return Result("Ah! The ship's instruction manual. You'd feel better"
                      " if the previous owner wasn't lying next to it with a"
                      " gaping hole in his rib cage.")


class Manual(Item):
    "A ship instruction manual."

    INVENTORY_IMAGE = "manual.png"
    CURSOR = None

    def is_interactive(self, tool=None):
        return True

    def interact_without(self):
        return Result(detail_view='manual_detail')


SCENES = [Machine]
