"""Engine room where things need to be repaired."""

from gamelib.cursor import CursorSprite
from gamelib.state import Scene, Item, Thing, Result
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractAnimated, GenericDescThing)


class Engine(Scene):

    FOLDER = "engine"
    BACKGROUND = "engine_room.png"

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Engine, self).__init__(state)
        self.add_item(CanOpener('canopener'))
        self.add_thing(CanOpenerThing())
        self.add_item(BrokenSuperconductor('superconductor_broken'))
        self.add_thing(SuperconductorSocket())
        self.add_thing(ToMap())
        self.add_thing(GenericDescThing('engine.body', 1,
            "Dead. He must have suffocated in the vacuum.",
            (
                (594, 387, 45, 109),
                (549, 475, 60, 55),
            )
        ))
        self.add_thing(GenericDescThing('engine.controlpanel', 1,
            "A control panel. It seems dead.",
            (
                (513, 330, 58, 50),
            )
        ))
        self.add_thing(GenericDescThing('engine.computer_console', 1,
            "A computer console. It seems dead",
            (
                (293, 287, 39, 36),
            )
        ))
        self.add_thing(GenericDescThing('engine.superconductors', 1,
            "Superconductors. The engines must be power hogs.",
            (
                (679, 246, 50, 56),
                (473, 277, 28, 23),
                (381, 224, 26, 22),
            )
        ))
        self.add_thing(GenericDescThing('engine.floor_hole', 1,
            "A gaping hole in the floor of the room. I'm guessing that's why there's a vacuum in here.",
            (
                (257, 493, 141, 55),
                (301, 450, 95, 45),
                (377, 422, 19, 29),
                (239, 547, 123, 39),
            )
        ))
        self.add_thing(GenericDescThing('engine.cryo_containers', 1,
            "Those are cryo-fluid containers. They look empty",
            (
                (129, 246, 135, 160),
            )
        ))
        self.add_thing(GenericDescThing('engine.empty_cans', 1,
            "Empty Chocolate-Covered-Bacon Cans? He must have got in early",
            (
                (562, 422, 30, 31),
            )
        ))
        self.add_thing(GenericDescThing('engine.engines', 1,
            "The engines. They don't look like they are working.",
            (
                (342, 261, 109, 81),
            )
        ))
        self.add_thing(GenericDescThing('engine.laser_cutter', 1,
            "A burned out laser cutter. It may be responsible for the hole in the floor.",
            (
                (120, 466, 115, 67),
            )
        ))
        self.add_thing(GenericDescThing('engine.spare_fuel_line', 1,
            "The spare fuel line. If something went wrong with the main one, you would hook that one up.",
            (
                (512, 49, 68, 44),
            )
        ))


    def enter(self):
        return Result("You enter the engine room. Even if there wasn't a vacuum "
                      "it would be errily quiet.")

class CanOpener(Item):
    INVENTORY_IMAGE = 'triangle.png'
    CURSOR = CursorSprite('triangle.png', 25, 23)


class CanOpenerThing(Thing):
    NAME = 'engine.canopener'

    INTERACTS = {
        'canopener': InteractImage(565, 456, 'can_opener.png'),
    }

    INITIAL = 'canopener'

    def get_description(self):
        return "A can opener. Looks like you won't be starving"

    def interact_without(self):
        self.state.add_inventory_item('canopener')
        self.scene.remove_thing(self)
        return Result("You pick up the can opener. It looks brand new, "
                      "the vacuum has kept it in perfect condition.")


class BrokenSuperconductor(Item):
    INVENTORY_IMAGE = 'superconductor_broken.png'
    CURSOR = CursorSprite('superconductor_broken_cursor.png', 13, 19)


class SuperconductorSocket(Thing):
    NAME = 'engine.superconductor'

    INTERACTS = {
        'broken': InteractImage(565, 263, 'superconductor_broken.png'),
        'removed': InteractNoImage(565, 263, 26, 39),
        'fixed': InteractImage(565, 263, 'superconductor_fixed.png'),
    }

    INITIAL = 'broken'

    INITIAL_DATA = {
        'present': True,
        'working': False,
    }

    def get_description(self):
        if self.get_data('present') and not self.get_data('working'):
            return "That superconductor looks burned out. It's wedged in there pretty firmly"
        elif not self.get_data('present'):
            return "An empty superconductor socket"
        else:
            return "A working superconductor."

    def interact_without(self):
        if self.get_data('present') and not self.get_data('working'):
            return Result("It's wedged in there pretty firmly, it won't come out.")
        elif self.get_data('working'):
            return Result("You decide that working engines are more important than having a shiny superconductor")
        Thing.interact_without()

    def interact_with_machete(self, item):
        if self.get_data('present') and not self.get_data('working'):
            self.set_interact('removed')
            self.set_data('present', False)
            self.state.add_inventory_item('superconductor_broken')
            return Result("With leverage, the burned-out superconductor snaps out.")
        Thing.interact_without()

    def interact_with_superconductor(self, item):
        if not self.get_data('present'):
            self.set_interact('fixed')
            self.set_data('present', True)
            self.set_data('working', True)
            self.state.remove_inventory_item(item.name)
            return Result("The chair's superconductor looks over-specced for this job, but it should work")
        else:
            return Result("It might help to remove the broken superconductor first")


class ToMap(Door):

    SCENE = "engine"

    INTERACTS = {
        "door": InteractNoImage(663, 360, 108, 193),
        }

    INITIAL = "door"

    def get_description(self):
        return "The airlock leads back to the rest of the ship."

SCENES = [Engine]
