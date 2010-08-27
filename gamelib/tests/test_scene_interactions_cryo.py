import game_logic_utils


class TestGameLogic(game_logic_utils.GameLogicTestCase):

    CURRENT_SCENE = 'cryo'

    def test_cryo_door_closed_hand(self):
        "The door is closed and we touch it with the hand. It becomes ajar."

        self.assert_game_data('door', 'shut', 'cryo.door')

        self.interact_thing('cryo.door')

        self.assert_game_data('door', 'ajar', 'cryo.door')

    def test_cryo_door_closed_titanium_leg(self):
        "The door is closed and we touch it with the titanium leg. It opens."

        self.state.add_inventory_item('titanium_leg')
        self.assert_game_data('door', 'shut', 'cryo.door')

        self.interact_thing('cryo.door', 'titanium_leg')

        self.assert_game_data('door', 'shut', 'cryo.door')
        self.assert_inventory_item('titanium_leg', True)

    def test_cryo_door_ajar_hand(self):
        "The door is ajar and we touch it with the hand. No change."

        self.set_game_data('door', 'ajar', 'cryo.door')

        self.interact_thing('cryo.door')

        self.assert_game_data('door', 'ajar', 'cryo.door')

    def test_cryo_door_ajar_titanium_leg(self):
        "The door is ajar and we touch it with the titanium leg. It opens."

        self.state.add_inventory_item('titanium_leg')
        self.set_game_data('door', 'ajar', 'cryo.door')

        self.interact_thing('cryo.door', 'titanium_leg')

        self.assert_game_data('door', 'open', 'cryo.door')
        self.assert_inventory_item('titanium_leg', True)

    def test_cryo_door_open_hand(self):
        "The door is open and we touch it with the hand. We go to the map."

        self.set_game_data('door', 'open', 'cryo.door')

        self.interact_thing('cryo.door')

        self.assert_game_data('door', 'open', 'cryo.door')
        self.assertEquals('map', self.state.current_scene.name)

    def test_cryo_door_open_titanium_leg(self):
        "The door is open and we touch it with the titanium leg. No change."

        self.set_game_data('door', 'open', 'cryo.door')

        self.interact_thing('cryo.door', 'titanium_leg')

        self.assert_game_data('door', 'open', 'cryo.door')
        self.assertEquals('cryo', self.state.current_scene.name)

    def test_cryo_unit_alpha_full_hand(self):
        "The cryo unit has the leg in it and we touch it. We get the leg."

        self.state.set_current_detail('cryo_detail')
        self.assert_game_data('contains_titanium_leg', True, 'cryo.unit.1')
        self.assert_inventory_item('titanium_leg', False)
        self.assert_detail_thing('cryo.titanium_leg', True)

        self.interact_thing('cryo.titanium_leg', detail='cryo_detail')

        self.assert_game_data('contains_titanium_leg', False, 'cryo.unit.1')
        self.assert_inventory_item('titanium_leg', True)
        self.assert_detail_thing('cryo.titanium_leg', False)

    def test_cryo_unit_detail(self):
        "The cryo unit thing opens a detail window."

        resp = self.interact_thing('cryo.unit.1')

        self.assertEquals('cryo_detail', resp.detail_view)

    def test_pipes_unchopped_hand(self):
        "Touch the unchopped cryopipes with the hand. No change."

        self.assert_game_data('fixed', True, 'cryo.pipe.left')
        self.assert_game_data('fixed', True, 'cryo.pipe.right')

        self.assertNotEquals(None, self.interact_thing('cryo.pipe.left'))
        self.assertNotEquals(None, self.interact_thing('cryo.pipe.right'))

        self.assert_game_data('fixed', True, 'cryo.pipe.left')
        self.assert_game_data('fixed', True, 'cryo.pipe.right')

    def test_pipes_chopped_hand(self):
        "Touch the chopped cryopipes with the hand. No change."

        self.set_game_data('fixed', False, 'cryo.pipe.left')
        self.set_game_data('fixed', False, 'cryo.pipe.right')

        self.assertEquals(None, self.interact_thing('cryo.pipe.left'))
        self.assertEquals(None, self.interact_thing('cryo.pipe.right'))

        self.assert_game_data('fixed', False, 'cryo.pipe.left')
        self.assert_game_data('fixed', False, 'cryo.pipe.right')

    def test_pipes_unchopped_machete(self):
        "Touch the unchopped cryopipes with the machete. They chop."

        self.assert_game_data('fixed', True, 'cryo.pipe.left')
        self.assert_game_data('fixed', True, 'cryo.pipe.right')
        self.assert_item_exists('cryo_pipe.0', False)
        self.assert_item_exists('cryo_pipe.1', False)

        self.assertNotEquals(None, self.interact_thing('cryo.pipe.left', 'machete'))
        self.assertNotEquals(None, self.interact_thing('cryo.pipe.right', 'machete'))

        self.assert_game_data('fixed', False, 'cryo.pipe.left')
        self.assert_game_data('fixed', False, 'cryo.pipe.right')
        self.assert_item_exists('cryo_pipe.0')
        self.assert_item_exists('cryo_pipe.1')
        self.assert_inventory_item('cryo_pipe.0', True)
        self.assert_inventory_item('cryo_pipe.1', True)

    def test_pipes_chopped_machete(self):
        "Touch the chopped cryopipes with the machete. No change."

        self.set_game_data('fixed', False, 'cryo.pipe.left')
        self.set_game_data('fixed', False, 'cryo.pipe.right')

        self.assertEquals(None, self.interact_thing('cryo.pipe.left', 'machete'))
        self.assertEquals(None, self.interact_thing('cryo.pipe.right', 'machete'))

        self.assert_game_data('fixed', False, 'cryo.pipe.left')
        self.assert_game_data('fixed', False, 'cryo.pipe.right')
