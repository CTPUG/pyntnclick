"""Neurally implanted schematic for moving around on the ship.

   It is illegal for prisoners in transit to activate such an
   implant. Failure to comply carries a minimum sentence of
   six months.

   Many parts of the ship are derelict and inaccessible.
   """

from gamelib.state import Scene, Item, Thing


class Map(Scene):

    FOLDER = "map"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        }


SCENES = [Map]
