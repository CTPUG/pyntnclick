from gamelib.state import Scene, Item

class Cryo(Scene):

    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"

    def __init__(self, state):
        super(Cryo, self).__init__(state)
        self.add_item(Triangle("triangle"))
        self.add_item(Square("square"))


class Triangle(Item):

    INVENTORY_IMAGE = "triangle.png"


class Square(Item):

    INVENTORY_IMAGE = "square.png"


SCENES = [Cryo]
