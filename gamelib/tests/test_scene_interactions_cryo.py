import game_logic_utils


class TestGameLogic(game_logic_utils.GameLogicTestCase):

    CURRENT_SCENE = 'cryo'

    def test_cryo_door_closed_hand(self):
        "The door is closed and we touch it with the hand. No change."

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('open', False, 'cryo.door')

        self.interact_thing('cryo.door')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('open', False, 'cryo.door')

    def test_cryo_door_closed_titanium_leg(self):
        "The door is closed and we touch it with the titanium leg. It opens."

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('open', False, 'cryo.door')

        self.interact_thing('cryo.door', 'titanium_leg')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', True, scene='bridge')
        self.assert_game_data('open', True, 'cryo.door')

    def test_cryo_door_open_hand(self):
        "The door is open and we touch it with the hand. No change."

        self.set_game_data('accessible', True, scene='bridge')
        self.set_game_data('open', True, 'cryo.door')

        self.interact_thing('cryo.door')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', True, scene='bridge')
        self.assert_game_data('open', True, 'cryo.door')

    def test_cryo_door_open_titanium_leg(self):
        "The door is open and we touch it with the titanium leg. No change."

        self.set_game_data('accessible', True, scene='bridge')
        self.set_game_data('open', True, 'cryo.door')

        self.interact_thing('cryo.door', 'titanium_leg')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', True, scene='bridge')
        self.assert_game_data('open', True, 'cryo.door')
