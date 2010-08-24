import game_logic_utils


class TestGameLogic(game_logic_utils.GameLogicTestCase):

    CURRENT_SCENE = 'cryo'

    def test_cryo_door_closed_hand(self):
        "The door is closed and we touch it with the hand. It becomes ajar."

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('door', 'shut', 'cryo.door')

        self.interact_thing('cryo.door')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('door', 'ajar', 'cryo.door')

    def test_cryo_door_closed_titanium_leg(self):
        "The door is closed and we touch it with the titanium leg. It opens."

        self.state.add_inventory_item('titanium_leg')
        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('door', 'shut', 'cryo.door')

        self.interact_thing('cryo.door', 'titanium_leg')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('door', 'shut', 'cryo.door')
        self.assert_inventory_item('titanium_leg', True)

    def test_cryo_door_ajar_hand(self):
        "The door is ajar and we touch it with the hand. No change."

        self.set_game_data('door', 'ajar', 'cryo.door')
        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')

        self.interact_thing('cryo.door')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')
        self.assert_game_data('door', 'ajar', 'cryo.door')

    def test_cryo_door_ajar_titanium_leg(self):
        "The door is ajar and we touch it with the titanium leg. It opens."

        self.state.add_inventory_item('titanium_leg')
        self.set_game_data('door', 'ajar', 'cryo.door')
        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', False, scene='bridge')

        self.interact_thing('cryo.door', 'titanium_leg')

        self.assert_game_data('accessible', True)
        self.assert_game_data('accessible', True, scene='bridge')
        self.assert_game_data('door', 'open', 'cryo.door')
        self.assert_inventory_item('titanium_leg', False)

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

    def test_cryo_unit_alpha_full_hand(self):
        "The cryo unit has the leg in it and we touch it. We get the leg."

        self.assert_game_data('contains_titanium_leg', True, 'cryo.unit.1')
        self.assert_inventory_item('titanium_leg', False)

        self.interact_thing('cryo.unit.1')

        self.assert_game_data('contains_titanium_leg', False, 'cryo.unit.1')
        self.assert_inventory_item('titanium_leg', True)
