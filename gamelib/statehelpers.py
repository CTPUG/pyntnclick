"""Set of utility classes for common state things"""

from pygame.color import Color
from pygame.colordict import THECOLORS

from gamelib.state import Thing, Result, \
                          InteractImage, InteractNoImage, InteractRectUnion, \
                          InteractAnimated
from gamelib.constants import DEBUG


class GenericDescThing(Thing):
    "Thing with an InteractiveUnionRect and a description"

    INITIAL = "description"

    def __init__(self, prefix, number, description, areas):
        super(GenericDescThing, self).__init__()
        self.description = description
        self.name = '%s.%s' % (prefix, number)
        self.interacts = {
                'description' : InteractRectUnion(areas)
                }
        if DEBUG:
            # Individual colors to make debugging easier
            self._interact_hilight_color = Color(THECOLORS.keys()[number])

    def get_description(self):
        return self.description

