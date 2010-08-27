import game_logic_utils


class TestWalkthrough(game_logic_utils.GameLogicTestCase):

    CURRENT_SCENE = 'cryo'

    def close_detail(self):
        self.state.set_current_detail(None)

    def move_to(self, target):
        self.interact_thing(self.state.current_scene.name + '.door')
        self.assert_current_scene('map')
        self.interact_thing('map.to' + target)
        self.assert_current_scene(target)

    def test_walkthrough_complete(self):
        self.fail("Walkthrough incomplete.")

    def test_walkthrough(self):
        """A complete game walkthrough.

        This should only contain interacts and assertions."""

        # TODO: Add flavour interactions, maybe?

        # Partially open the door.
        self.assert_game_data('door', 'shut', 'cryo.door')
        self.interact_thing('cryo.door')
        self.assert_game_data('door', 'ajar', 'cryo.door')

        # Get the titanium leg.
        self.interact_thing('cryo.unit.1')
        self.assertEquals('cryo_detail', self.state.current_detail.name)
        self.assert_detail_thing('cryo.titanium_leg')
        self.interact_thing('cryo.titanium_leg')
        self.assert_detail_thing('cryo.titanium_leg', False)
        self.assert_inventory_item('titanium_leg')
        self.close_detail()

        # Open the door the rest of the way.
        self.interact_thing('cryo.door', 'titanium_leg')
        self.assert_game_data('door', 'open', 'cryo.door')
        self.assert_inventory_item('titanium_leg')

        # Go to the mess.
        self.move_to('mess')

        # Get the cans.
        self.assert_game_data('cans_available', 3, 'mess.cans')
        self.interact_thing('mess.cans')
        self.assert_inventory_item('full_can.0')
        self.interact_thing('mess.cans')
        self.assert_inventory_item('full_can.1')
        self.interact_thing('mess.cans')
        self.assert_inventory_item('full_can.2')
        self.assert_game_data('cans_available', 0, 'mess.cans')

        # Bash one of the cans.
        self.assert_item_exists('dented_can.0', False)
        self.interact_item('full_can.1', 'titanium_leg')
        self.assert_inventory_item('dented_can.0')
        self.assert_inventory_item('full_can.1', False)

        # Go to the machine room.
        self.move_to('machine')

        # Sharpen leg into machete.
        self.interact_thing('machine.grinder', 'titanium_leg')
        self.assert_inventory_item('titanium_leg', False)
        self.assert_inventory_item('machete')

        # Go to the cryo room.
        self.move_to('cryo')

        # Chop up some pipes.
        self.assert_game_data('fixed', True, 'cryo.pipe.left')
        self.interact_thing('cryo.pipe.left', 'machete')
        self.assert_game_data('fixed', False, 'cryo.pipe.left')
        self.assert_inventory_item('cryo_pipe.0')

        self.assert_game_data('fixed', True, 'cryo.pipe.right')
        self.interact_thing('cryo.pipe.right', 'machete')
        self.assert_game_data('fixed', False, 'cryo.pipe.right')
        self.assert_inventory_item('cryo_pipe.1')

        # Go to the mess.
        self.move_to('mess')

        # Clear the broccoli.
        self.assert_game_data('status', 'blocked', 'mess.tubes')
        self.interact_thing('mess.tubes', 'machete')
        self.assert_game_data('status', 'broken', 'mess.tubes')

