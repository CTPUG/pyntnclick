"""Generic, game specific widgets"""

import random

from gamelib.state import Thing, Result


class Door(Thing):
    """A door somewhere"""

    DEST = "map"

    def is_interactive(self):
        return True

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")

    def get_description(self):
        return 'An open doorway leads to the rest of the ship.'

    def interact_default(self, item):
        return Result(random.choice([
            "Sadly, this isn't that sort of game.",
            "Your valiant efforts are foiled by the Evil Game Designer.",
            "Waving that in the doorway does nothing. Try something else, perhaps?",
            ]))

