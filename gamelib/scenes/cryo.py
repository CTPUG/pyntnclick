from gamelib.state import Scene

class Cryo(Scene):

    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"

    def __init__(self, state):
        super(Cryo, self).__init__(state)


SCENES = [Cryo]
