"""Cryo room where the prisoner starts out."""

from gamelib.state import Scene, Item, Thing


class Cryo(Scene):

    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"

    def __init__(self, state):
        super(Cryo, self).__init__(state)
        self.add_item(Triangle("triangle"))
        self.add_item(Square("square"))
        self.add_thing(CryoUnitAlpha("cryo.unit.1", (20, 20, 400, 500)))


class Triangle(Item):
    INVENTORY_IMAGE = "triangle.png"


class Square(Item):
    INVENTORY_IMAGE = "square.png"


class CryoUnitAlpha(Thing):
    pass


SCENES = [Cryo]
