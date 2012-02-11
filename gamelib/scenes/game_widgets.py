"""Generic, game specific widgets"""


from pyntnclick.state import Thing, Result


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
        self.game.set_current_scene("map")

    def get_description(self):
        return 'An open doorway leads to the rest of the ship.'

    def interact_default(self, item):
        return self.interact_without()


def make_jim_dialog(mesg, state):
    "Utility helper function"
    if state.scenes['bridge'].get_data('ai status') == 'online':
        return Result(mesg, style='JIM')
    else:
        return None


class BaseCamera(Thing):
    "Base class for the camera puzzles"

    INITIAL = 'online'
    INITIAL_DATA = {
         'state': 'online',
    }

    def get_description(self):
        status = self.game.scenes['bridge'].get_data('ai status')
        if status == 'online':
            return "A security camera watches over the room"
        elif status == 'looping':
            return "The security camera is currently offline but should be" \
                    " working soon"
        else:
            return "The security camera is powered down"

    def is_interactive(self, tool=None):
        return self.game.scenes['bridge'].get_data('ai status') == 'online'

    def interact_with_escher_poster(self, item):
        # Order matters here, because of helper function
        if self.game.scenes['bridge'].get_data('ai status') == 'online':
            ai_response = make_jim_dialog("3D scene reconstruction failed."
                    " Critical error. Entering emergency shutdown.",
                    self.game)
            self.game.scenes['bridge'].set_data('ai status', 'looping')
            return ai_response

    def animate(self):
        ai_status = self.game.scenes['bridge'].get_data('ai status')
        if ai_status != self.get_data('status'):
            self.set_data('status', ai_status)
            self.set_interact(ai_status)
        super(BaseCamera, self).animate()
