"""Neurally implanted schematic for moving around on the ship.

   It is illegal for prisoners in transit to activate such an
   implant. Failure to comply carries a minimum sentence of
   six months.

   Many parts of the ship are derelict and inaccessible.
   """

from gamelib.state import Scene, Item, Thing, Result
from gamelib.scenes.game_constants import PLAYER_ID
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractAnimated, GenericDescThing)


class Map(Scene):

    FOLDER = "map"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        'implant': True,
        }

    def __init__(self, state):
        super(Map, self).__init__(state)
        self.add_thing(ToCryo())
        self.add_thing(ToBridge())
        self.add_thing(ToMess())
        self.add_thing(ToEngine())
        self.add_thing(ToMachine())
        self.add_thing(ToCrew())

    def enter(self):
        for door_thing in self.things.values():
            door_thing.check_dest()
        if self.get_data('implant'):
            self.set_data('implant', False)
            return (Result(
                "JIM says: 'Under the terms of the emergency conscription "
                "act, I have downloaded the ship's schematics to your "
                "neural implant to help you navigate around the ship. "
                "Please report to the bridge.'", style="JIM"),
                Result(
                "JIM continues: 'Prisoner %s. You are classed "
                "as a class 1 felon. Obtaining access to the ship's schematics "
                "constitutes a level 2 offence and carries a minimal penalty "
                "of an additional 3 years on your sentence.'" % PLAYER_ID,
                style="JIM"))


class DoorThing(Thing):

    # name of destination
    DEST = None

    def interact_without(self):
        """Go to destination."""
        if self.DEST in self.state.scenes:
            if self.state.scenes[self.DEST].get_data('accessible'):
                self.state.set_current_scene(self.DEST)
                return Result()
            else:
                return Result("You can't go there right now.")
        else:
            return Result("You *could* go there, but it doesn't actually exist.")

    def check_dest(self):
        if self.DEST in self.state.scenes:
            if self.state.scenes[self.DEST].get_data('accessible'):
                self.set_interact('accessible')
            else:
                self.set_interact('inaccessible')


class ToCryo(DoorThing):
    "Way to cryo room."

    NAME = "map.tocryo"
    DEST = "cryo"

    INTERACTS = {
        "inaccessible": InteractText(100, 200, "To Cryo"),
        "accessible": InteractText(100, 200, "To Cryo", (0, 127, 0)),
        }

    INITIAL = "inaccessible"


class ToBridge(DoorThing):
    "Way to bridge room."

    NAME = "map.tobridge"
    DEST = "bridge"

    INTERACTS = {
        "inaccessible": InteractText(300, 200, "To Bridge"),
        "accessible": InteractText(300, 200, "To Bridge", (0, 127, 0)),
        }

    INITIAL = "inaccessible"


class ToMess(DoorThing):
    "Way to cryo room."

    NAME = "map.tomess"
    DEST = "mess"

    INTERACTS = {
        "inaccessible": InteractText(100, 300, "To Mess"),
        "accessible": InteractText(100, 300, "To Mess", (0, 127, 0)),
        }

    INITIAL = "inaccessible"


class ToEngine(DoorThing):
    "Way to engine room."

    NAME = "map.toengine"
    DEST = "engine"

    INTERACTS = {
        "inaccessible": InteractText(300, 300, "To Engine"),
        "accessible": InteractText(300, 300, "To Engine", (0, 127, 0)),
        }

    INITIAL = "inaccessible"

    def interact_without(self):
        if not self.state.is_in_inventory('helmet'):
            return Result('The airlock refuses to open. The automated'
                    ' voice says "Hull breach beyond this door. Personnel'
                    ' must be equipped for vacuum before entry"')
        else:
            return super(ToEngine, self).interact_without()


class ToMachine(DoorThing):
    "Way to machine room."

    NAME = "map.tomachine"
    DEST = "machine"

    INTERACTS = {
        "inaccessible": InteractText(100, 400, "To Machine"),
        "accessible": InteractText(100, 400, "To Machine", (0, 127, 0)),
        }

    INITIAL = "inaccessible"


class ToCrew(DoorThing):
    "Way to crew quarters."

    NAME = "map.tocrew_quarters"
    DEST = "crew_quarters"

    INTERACTS = {
        "inaccessible": InteractText(300, 400, "To Crew Quarters"),
        "accessible": InteractText(300, 400, "To Crew Quarters", (0, 127, 0)),
        }

    INITIAL = "inaccessible"


SCENES = [Map]
