"""Neurally implanted schematic for moving around on the ship.

   It is illegal for prisoners in transit to activate such an
   implant. Failure to comply carries a minimum sentence of
   six months.

   Many parts of the ship are derelict and inaccessible.
   """

from gamelib.state import Scene, Item, Thing, InteractText


class Map(Scene):

    FOLDER = "map"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Map, self).__init__(state)
        self.add_thing(ToCryo())
        self.add_thing(ToBridge())
        self.add_thing(ToMess())
        self.add_thing(ToEngine())
        self.add_thing(ToMachine())


class ToCryo(Thing):
    "Way to cryo room."

    NAME = "map.tocryo"

    INTERACTS = {
        "room": InteractText(100, 200, "To Cryo"),
        }

    INITIAL = "room"


class ToBridge(Thing):
    "Way to bridge room."

    NAME = "map.tobridge"

    INTERACTS = {
        "room": InteractText(300, 200, "To Bridge"),
        }

    INITIAL = "room"


class ToMess(Thing):
    "Way to cryo room."

    NAME = "map.tomess"

    INTERACTS = {
        "room": InteractText(100, 300, "To Mess"),
        }

    INITIAL = "room"


class ToEngine(Thing):
    "Way to engine room."

    NAME = "map.toengine"

    INTERACTS = {
        "room": InteractText(300, 300, "To Engine"),
        }

    INITIAL = "room"


class ToMachine(Thing):
    "Way to machine room."

    NAME = "map.tomachine"

    INTERACTS = {
        "room": InteractText(100, 400, "To Machine"),
        }

    INITIAL = "room"


SCENES = [Map]
