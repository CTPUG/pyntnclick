from pyntnclick.tests.mad_clicker import MadClickerTestCase

import gamelib.main


class SSMadClicker(MadClickerTestCase):

    GAME_DESCRIPTION_CLASS = gamelib.main.SuspendedSentence
    CURRENT_SCENE = 'cryo'

    def test_mad_clicker(self):
        self.do_mad_clicker()
