"""Generic, game specific widgets"""


from pyntnclick.state import Thing, Result

from gamelib.custom_widgets import JimLabel


class Door(Thing):
    """A door somewhere"""

    DEST = "map"
    SCENE = None

    def __init__(self):
        self.NAME = self.SCENE + '.door'
        Thing.__init__(self)

    def is_interactive(self, tool=None):
        return True

    def interact_without(self):
        """Go to map."""
        self.game.change_scene("map")

    def get_description(self):
        return 'An open doorway leads to the rest of the ship.'

    def interact_default(self, item):
        return self.interact_without()


def make_jim_dialog(mesg, game):
    "Utility helper function"
    if game.data.get_jim_state() == 'online':
        return Result(widget=JimLabel(game.gd, mesg))
    else:
        return None


class BaseCamera(Thing):
    "Base class for the camera puzzles"

    INITIAL = 'online'
    INITIAL_DATA = {
         'state': 'online',
    }

    def get_description(self):
        status = self.state.get_jim_state()
        if status == 'online':
            return "A security camera watches over the room"
        elif status == 'looping':
            return "The security camera is currently offline but should be" \
                    " working soon"
        else:
            return "The security camera is powered down"

    def is_interactive(self, tool=None):
        return self.state.get_jim_state() == 'online'

    def interact_with_escher_poster(self, item):
        # Order matters here, because of helper function
        if self.state.get_jim_state() == 'online':
            ai_response = make_jim_dialog("3D scene reconstruction failed."
                    " Critical error. Entering emergency shutdown.",
                    self.game)
            self.game.data.loop_ai()
            return ai_response

    def select_interact(self):
        if 'bridge' not in self.state:
            # We aren't completely set up yet
            return self.INITIAL
        return self.state.get_jim_state()

    def animate(self):
        ai_status = self.state.get_jim_state()
        if ai_status != self.get_data('status'):
            self.set_data('status', ai_status)
            self.set_interact()
        super(BaseCamera, self).animate()
