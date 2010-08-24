"""Machine room where tools and machines are found."""

from gamelib.state import Scene, Item, Thing, InteractText, Result


class Machine(Scene):

    FOLDER = "machine"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Machine, self).__init__(state)
        self.add_thing(ToMap())

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


SCENES = [Machine]
