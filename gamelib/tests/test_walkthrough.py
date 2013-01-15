import game_logic_utils


class TestWalkthrough(game_logic_utils.GameLogicTestCase):

    CURRENT_SCENE = 'cryo'

    def move_to(self, target):
        self.interact_thing(self.state.current_scene.name + '.door')
        self.assert_current_scene('map')
        self.interact_thing('map.to' + target)
        self.assert_current_scene(target)

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
        self.assert_current_detail('cryo_detail')
        self.assert_detail_thing('cryo.titanium_leg')
        self.interact_thing('cryo.titanium_leg', detail='cryo_detail')
        self.assert_detail_thing('cryo.titanium_leg', False)
        self.assert_inventory_item('titanium_leg')
        self.close_detail()

        # Open the door the rest of the way.
        self.interact_thing('cryo.door', 'titanium_leg')
        self.assert_game_data('door', 'open', 'cryo.door')
        self.assert_inventory_item('titanium_leg')

        # Go to the mess.
        self.move_to('mess')

        # Check that life support is broken
        self.assert_game_data('life support status', 'broken')

        # Get the cans.
        self.assert_game_data('cans_available', 3, 'mess.cans')
        self.interact_thing('mess.cans')
        self.assert_inventory_item('full_can.0')
        self.assert_game_data('cans_available', 2, 'mess.cans')
        self.interact_thing('mess.cans')
        self.assert_inventory_item('full_can.1')
        self.assert_game_data('cans_available', 1, 'mess.cans')
        self.interact_thing('mess.cans')
        self.assert_inventory_item('full_can.2')
        self.assert_scene_thing('mess.cans', False)

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
        self.assert_inventory_item('tube_fragment.0')

        self.assert_game_data('fixed', True, 'cryo.pipe.right.top')
        self.interact_thing('cryo.pipe.right.top', 'machete')
        self.assert_game_data('fixed', False, 'cryo.pipe.right.top')
        self.assert_inventory_item('tube_fragment.1')

        self.assert_game_data('fixed', True, 'cryo.pipe.right.bottom')
        self.interact_thing('cryo.pipe.right.bottom', 'machete')
        self.assert_game_data('fixed', False, 'cryo.pipe.right.bottom')
        self.assert_inventory_item('tube_fragment.2')

        # Go to the mess.
        self.move_to('mess')

        # Clear the broccoli.
        self.assert_game_data('status', 'blocked', 'mess.tubes')
        self.interact_thing('mess.tubes', 'machete')
        self.assert_game_data('status', 'broken', 'mess.tubes')

        # Go to the bridge.
        self.move_to('bridge')

        # Check that the AI is online.
        self.assert_game_data('ai status', 'online')

        # Get the stethoscope.
        self.interact_thing('bridge.stethoscope')
        self.assert_inventory_item('stethoscope')
        self.assert_scene_thing('bridge.stethoscope', False)

        # Get the superconductor.
        self.interact_thing('bridge.massagechair_base')
        self.assert_current_detail('chair_detail')
        self.interact_thing('bridge.superconductor', detail='chair_detail')
        self.assert_inventory_item('superconductor')
        self.assert_detail_thing('bridge.superconductor', False)
        self.close_detail()

        # Go to the crew quarters.
        self.move_to('crew_quarters')

        # Get the poster.
        self.interact_thing('crew.poster')
        self.assert_inventory_item('escher_poster')
        self.assert_scene_thing('crew.poster', False)

        # Get the fishbowl.
        self.assert_game_data('has_bowl', True, 'crew.fishbowl')
        self.interact_thing('crew.fishbowl')
        self.assert_game_data('has_bowl', False, 'crew.fishbowl')
        self.assert_inventory_item('fishbowl')

        # Crack the safe.
        self.assert_game_data('is_cracked', False, 'crew.safe')
        self.interact_thing('crew.safe', 'stethoscope')
        self.assert_game_data('is_cracked', True, 'crew.safe')

        # Get the duct tape.
        self.assert_game_data('has_tape', True, 'crew.safe')
        self.interact_thing('crew.safe')
        self.assert_game_data('has_tape', False, 'crew.safe')
        self.assert_inventory_item('duct_tape')

        # Make the helmet.
        self.interact_item('fishbowl', 'duct_tape')
        self.assert_inventory_item('helmet')
        self.assert_inventory_item('fishbowl', False)

        # Go to the engine room.
        self.move_to('engine')

        # Check that the engines are broken.
        self.assert_game_data('engine online', False)

        # Get the can opener.
        self.interact_thing('engine.canopener')
        self.assert_inventory_item('canopener')
        self.assert_scene_thing('engine.canopener', False)

        # Open the cans.
        self.interact_item('full_can.2', 'canopener')
        self.assert_inventory_item('full_can.2', False)
        self.assert_inventory_item('empty_can.0')

        self.interact_item('full_can.0', 'canopener')
        self.assert_inventory_item('full_can.0', False)
        self.assert_inventory_item('empty_can.1')

        self.interact_item('dented_can.0', 'canopener')
        self.assert_inventory_item('dented_can.0', False)
        self.assert_inventory_item('empty_can.2')

        # Go to the machine room.
        self.move_to('machine')

        # Weld pipes and cans.
        self.assert_game_data('contents', set(), 'machine.welder.slot')
        self.interact_thing('machine.welder.slot', 'tube_fragment.0')
        self.assert_inventory_item('tube_fragment.0', False)
        self.assert_game_data('contents', set(['tube']), 'machine.welder.slot')
        self.interact_thing('machine.welder.slot', 'empty_can.1')
        self.assert_inventory_item('empty_can.1', False)
        self.assert_game_data(
            'contents', set(['tube', 'can']), 'machine.welder.slot')
        self.interact_thing('machine.welder.button')
        self.assert_game_data('contents', set(), 'machine.welder.slot')
        self.assert_inventory_item('cryo_pipes_one')

        self.assert_game_data('contents', set(), 'machine.welder.slot')
        self.interact_thing('machine.welder.slot', 'tube_fragment.2')
        self.assert_inventory_item('tube_fragment.2', False)
        self.assert_game_data('contents', set(['tube']), 'machine.welder.slot')
        self.interact_thing('machine.welder.slot', 'empty_can.2')
        self.assert_inventory_item('empty_can.2', False)
        self.assert_game_data(
            'contents', set(['tube', 'can']), 'machine.welder.slot')
        self.interact_thing('machine.welder.button')
        self.assert_game_data('contents', set(), 'machine.welder.slot')
        self.assert_inventory_item('cryo_pipes_one', False)
        self.assert_inventory_item('cryo_pipes_two')

        self.assert_game_data('contents', set(), 'machine.welder.slot')
        self.interact_thing('machine.welder.slot', 'tube_fragment.1')
        self.assert_inventory_item('tube_fragment.1', False)
        self.assert_game_data('contents', set(['tube']), 'machine.welder.slot')
        self.interact_thing('machine.welder.slot', 'empty_can.0')
        self.assert_inventory_item('empty_can.0', False)
        self.assert_game_data(
            'contents', set(['tube', 'can']), 'machine.welder.slot')
        self.interact_thing('machine.welder.button')
        self.assert_game_data('contents', set(), 'machine.welder.slot')
        self.assert_inventory_item('cryo_pipes_two', False)
        self.assert_inventory_item('cryo_pipes_three')

        # Go to the mess.
        self.move_to('mess')

        # Replace the tubes.
        self.interact_thing('mess.tubes', 'cryo_pipes_three')
        self.assert_inventory_item('cryo_pipes_three', False)
        self.assert_game_data('status', 'replaced', 'mess.tubes')

        # Check that life support is replaced
        self.assert_game_data('life support status', 'replaced')

        # Tape up the tubes.
        self.interact_thing('mess.tubes', 'duct_tape')
        self.assert_game_data('status', 'fixed', 'mess.tubes')

        # Check that life support is fixed
        self.assert_game_data('life support status', 'fixed')

        # Get the detergent bottle.
        self.interact_thing('mess.detergent')
        self.assert_inventory_item('detergent_bottle')

        # Go to the cryo room.
        self.move_to('cryo')

        # Fill the detergent bottle.
        self.interact_thing('cryo.pool', 'detergent_bottle')
        self.assert_inventory_item('detergent_bottle', False)
        self.assert_inventory_item('full_detergent_bottle')

        # Go to the engine room.
        self.move_to('engine')

        # Patch the cracked pipe.
        self.assert_game_data('fixed', False, 'engine.cracked_pipe')
        self.interact_thing('engine.cracked_pipe', 'duct_tape')
        self.assert_game_data('fixed', True, 'engine.cracked_pipe')

        # Fill the cryofluid receptacles.
        self.assert_game_data('filled', False, 'engine.cryo_containers')
        self.interact_thing(
            'engine.cryo_container_receptacle', 'full_detergent_bottle')
        self.assert_game_data('filled', True, 'engine.cryo_containers')
        self.assert_inventory_item('full_detergent_bottle', False)

        # Remove the burned-out superconductor.
        self.assert_game_data('present', True, 'engine.superconductor')
        self.assert_game_data('working', False, 'engine.superconductor')
        self.interact_thing('engine.superconductor', 'machete')
        self.assert_game_data('present', False, 'engine.superconductor')
        self.assert_game_data('working', False, 'engine.superconductor')

        # Tape up new superconductor.
        self.interact_item('superconductor', 'duct_tape')
        self.assert_inventory_item('superconductor', False)
        self.assert_inventory_item('taped_superconductor')

        # Install superconductor.
        self.interact_thing('engine.superconductor', 'taped_superconductor')
        self.assert_inventory_item('taped_superconductor', False)
        self.assert_game_data('present', True, 'engine.superconductor')
        self.assert_game_data('working', True, 'engine.superconductor')

        # Check that we've fixed the engines.
        self.assert_game_data('engine online', True)

        # Go to the bridge.
        self.move_to('bridge')

        # Show JIM the poster.
        self.interact_thing('bridge.camera', 'escher_poster')
        self.assert_game_data('ai status', 'looping')

        # Get at JIM.
        self.assert_game_data('ai panel', 'closed')
        self.interact_thing('jim_panel', 'machete')
        self.assert_game_data('ai panel', 'open')

        # Break JIM.
        self.interact_thing('jim_panel', 'machete')
        self.assert_game_data('ai panel', 'broken')

        # Check that we've turned off JIM.
        self.assert_game_data('ai status', 'dead')

        # Bring up nav console.
        self.interact_thing('bridge.comp')
        self.assert_current_detail('bridge_comp_detail')
        self.interact_thing('bridge_comp.nav_tab', detail='bridge_comp_detail')
        self.assert_game_data('tab', 'nav', detail='bridge_comp_detail')

        # Go somewhere interesting.
        self.interact_thing('bridge_comp.nav_line2', detail='bridge_comp_detail')
