"""Engine room where things need to be repaired."""

from pyntnclick.cursor import CursorSprite
from pyntnclick.state import Scene, Item, Thing, Result
from pyntnclick.scenewidgets import (InteractNoImage, InteractRectUnion,
                                  InteractImage, InteractAnimated,
                                  GenericDescThing)

from gamelib.scenes.game_constants import PLAYER_ID
from gamelib.scenes.game_widgets import Door, make_jim_dialog


class Engine(Scene):

    FOLDER = "engine"
    BACKGROUND = "engine_room.png"

    INITIAL_DATA = {
        'engine online': False,
        'greet': True,
        }

    def setup(self):
        self.add_item(CanOpener('canopener'))
        self.add_thing(CanOpenerThing())
        self.add_thing(SuperconductorSocket())
        self.add_thing(PowerLines())
        self.add_thing(CryoContainers())
        self.add_thing(CryoContainerReceptacle())
        self.add_thing(CoolingPipes())
        self.add_thing(ArrowsTopLeft())
        self.add_thing(ArrowsBottomLeft())
        self.add_thing(ArrowsRight())
        self.add_thing(DangerSign())
        self.add_thing(Stars())
        self.add_thing(CrackedPipe())
        self.add_thing(ComputerConsole())
        self.add_thing(ToMap())
        self.add_thing(GenericDescThing('engine.body', 1,
            "Dead. Those cans must have been past their sell-by date.",
            (
                (594, 387, 45, 109),
                (549, 479, 60, 55),
            )
        ))
        self.add_thing(GenericDescThing('engine.superconductors', 4,
            "Superconductors. The engines must be power hogs.",
            (
                (679, 246, 50, 56),
                (473, 280, 28, 23),
                (381, 224, 25, 22),
            )
        ))
        self.add_thing(GenericDescThing('engine.floor_hole', 5,
            "A gaping hole in the floor of the room. "
            "It is clearly irreparable.",
            (
                (257, 493, 141, 55),
                (301, 450, 95, 45),
                (377, 422, 19, 29),
                (239, 547, 123, 39),
            )
        ))
        self.add_thing(GenericDescThing('engine.empty_cans', 7,
            "Empty chocolate-covered bacon cans? Poor guy, he must have"
            " found them irresistible.",
            (
                (562, 422, 30, 31),
            )
        ))
        self.add_thing(GenericDescThing('engine.engines', 8,
            "The engines. They don't look like they are working.",
            (
                (342, 261, 109, 81),
            )
        ))
        self.add_thing(GenericDescThing('engine.laser_cutter', 9,
            "A burned-out laser cutter. It may be responsible for the"
            " hole in the floor.",
            (
                (120, 466, 115, 67),
            )
        ))
        self.add_thing(GenericDescThing('engine.fuel_lines', 10,
            "The main fuel line for the engines.",
            (
                (220, 49, 59, 75),
                (239, 84, 51, 66),
                (271, 113, 28, 53),
                (285, 132, 26, 50),
                (299, 153, 22, 46),
                (321, 172, 167, 25),
                (308, 186, 36, 22),
                (326, 217, 30, 13),
                (336, 229, 28, 13),
                (343, 239, 21, 14),
                (446, 197, 33, 11),
                (424, 240, 21, 20),
                (418, 249, 19, 11),
                (438, 217, 30, 11),
                (435, 225, 18, 15),
            )
        ))
        self.add_thing(GenericDescThing('engine.spare_fuel_line', 11,
            "The spare fuel line. If something went wrong with the main"
            " one, you would hook that one up.",
            (
                (512, 49, 68, 44),
            )
        ))
        self.add_thing(GenericDescThing('engine.danger_area', 12,
            "The sign says DANGER. You would be wise to listen to it.",
            (
                (293, 343, 211, 46),
            )
        ))
        self.add_thing(GenericDescThing('engine.exit_sign', 13,
            "It's one of those glow-in-the-dark signs needed to satisfy the "
            "health and safety inspectors.",
            (
                (681, 322, 80, 33),
            )
        ))

    def engine_online_check(self):
        if self.things['engine.cryo_containers'].get_data('filled') \
                and  self.things['engine.superconductor'].get_data('working'):
            self.set_data('engine online', True)
            self.remove_thing(self.things['engine.engines.8'])
            self.add_thing(Engines())
            return make_jim_dialog("The engines are now operational. You have"
                                   "done a satisfactory job, Prisoner %s."
                                   % PLAYER_ID,
                                   self.game)

    def enter(self):
        if self.get_data('greet'):
            self.set_data('greet', False)
            return Result(
                    "With your improvised helmet, the automatic airlock allows"
                    " you into the engine room. Even if there wasn't a vacuum "
                    "it would be eerily quiet.")


class Engines(Thing):
    NAME = 'engine.engines'

    INTERACTS = {
        'on': InteractImage(334, 253, 'engine_on.png'),
    }

    INITIAL = 'on'

    def is_interactive(self, tool=None):
        return False

    def get_description(self):
        return "All systems are go! Or at least the engines are."


class CanOpener(Item):
    INVENTORY_IMAGE = 'can_opener.png'
    CURSOR = CursorSprite('can_opener_cursor.png')


class CanOpenerThing(Thing):
    NAME = 'engine.canopener'

    INTERACTS = {
        'canopener': InteractImage(565, 456, 'can_opener.png'),
    }

    INITIAL = 'canopener'

    def get_description(self):
        return "A can opener. Looks like you won't be starving"

    def interact_without(self):
        self.game.add_inventory_item('canopener')
        self.scene.remove_thing(self)
        return Result("You pick up the can opener. It looks brand new; "
                      "the vacuum has kept it in perfect condition.")


class SuperconductorSocket(Thing):
    NAME = 'engine.superconductor'

    INTERACTS = {
        'broken': InteractImage(553, 260, 'superconductor_broken.png'),
        'removed': InteractImage(553, 260, 'superconductor_socket.png'),
        'fixed': InteractImage(553, 260, 'superconductor_fixed.png'),
    }

    INITIAL = 'broken'

    INITIAL_DATA = {
        'present': True,
        'working': False,
    }

    def get_description(self):
        if self.get_data('present') and not self.get_data('working'):
            return ("That superconductor looks burned out. It's wedged"
                    " in there pretty firmly.")
        elif not self.get_data('present'):
            return "An empty superconductor socket"
        else:
            return "A working superconductor."

    def interact_without(self):
        if self.get_data('present') and not self.get_data('working'):
            return Result("It's wedged in there pretty firmly, it won't"
                          " come out.")
        elif self.get_data('working'):
            return Result("You decide that working engines are more important"
                          " than having a shiny superconductor.")

    def interact_with_machete(self, item):
        if self.get_data('present') and not self.get_data('working'):
            self.set_interact('removed')
            self.set_data('present', False)
            return Result("With leverage, the burned-out superconductor"
                          " snaps out. You discard it.")

    def interact_with_superconductor(self, item):
        if self.get_data('present'):
            return Result("It might help to remove the broken"
                          " superconductor first")
        else:
            return Result("You plug in the superconductor, and feel a hum "
                          "as things kick into life. "
                          "Unfortunately, it's the wrong size for the socket "
                          "and just falls out again when you let go.")

    def interact_with_taped_superconductor(self, item):
        if not self.get_data('present'):
            self.set_interact('fixed')
            self.set_data('present', True)
            self.set_data('working', True)
            self.game.remove_inventory_item(item.name)
            results = [Result("The chair's superconductor looks over-specced "
                              "for this job, but it should work.")]
            results.append(self.scene.engine_online_check())
            return results
        else:
            return Result("It might help to remove the broken superconductor"
                          " first.")


class CryoContainers(Thing):
    NAME = 'engine.cryo_containers'

    INTERACTS = {
        'empty': InteractImage(118, 211, 'cryo_empty.png'),
        'full': InteractImage(118, 211, 'cryo_full.png'),
        }

    INITIAL = 'empty'

    INITIAL_DATA = {
        'filled': False,
    }

    def get_description(self):
        if not self.get_data('filled'):
            return "Those are coolant reservoirs. They look empty."
        return "The coolant reservoirs are full."

    def is_interactive(self, tool=None):
        return False


class CryoContainerReceptacle(Thing):
    NAME = 'engine.cryo_container_receptacle'

    INTERACTS = {
        'containers': InteractRectUnion((
            (132, 250, 56, 28),
            (184, 258, 42, 30),
            (219, 267, 42, 24),
        )),
    }

    INITIAL = 'containers'

    def get_description(self):
        return "The receptacles for the coolant reservoirs."

    def interact_without(self):
        return Result("You stick your finger in the receptacle. "
                      "It almost gets stuck.")

    def interact_with_full_detergent_bottle(self, item):
        if not self.scene.things['engine.cracked_pipe'].get_data('fixed'):
            return Result("Pouring the precious cryo fluid into a"
                    " container connected to a cracked pipe would be a waste.")
        self.game.remove_inventory_item(item.name)
        self.scene.things['engine.cryo_containers'].set_data('filled', True)
        self.scene.things['engine.cryo_containers'].set_interact('full')
        results = [Result("You fill the reservoirs. "
                          "The detergent bottle was just big enough, which "
                          "is handy, because it's sprung a leak.")]
        results.append(self.scene.engine_online_check())
        return results


class CoolingPipes(Thing):
    NAME = 'engine.coolingpipes'

    INTERACTS = {
        'pipes': InteractRectUnion((
             (262, 209, 315, 7),
             (693, 155, 14, 90),
             (673, 138, 32, 27),
             (649, 155, 25, 21),
             (608, 177, 23, 18),
             (587, 186, 25, 18),
             (570, 195, 27, 20),
             (625, 167, 28, 18),
             (57, 86, 16, 238),
             (227, 188, 31, 49),
             (71, 91, 39, 36),
             (108, 117, 32, 69),
             (140, 135, 31, 64),
             (168, 156, 33, 57),
             (200, 172, 27, 55),
             (105, 159, 15, 289),
             (0, 309, 128, 16),
             (79, 390, 28, 22),
             (257, 209, 27, 10),
             (249, 225, 26, 20),
             (272, 237, 25, 17),
             (294, 247, 41, 24),
             (333, 254, 35, 6),
             (364, 235, 7, 25),
             (365, 231, 15, 13),
             (121, 403, 70, 38),
             (180, 392, 33, 19),
             (199, 383, 30, 18),
             (219, 378, 20, 10),
             (232, 370, 18, 11),
        )),
    }
    INITIAL = 'pipes'

    def get_description(self):
        if not self.scene.things['engine.cryo_containers'].get_data('filled'):
            return "These pipes carry coolant to the superconductors. " \
                   "They feel warm."
        return "These pipes carry coolant to the superconductors. " \
               "They are very cold."

    def is_interactive(self, tool=None):
        return False


class PowerLines(Thing):
    NAME = 'engine.powerlines'

    INTERACTS = {
        'lines': InteractRectUnion((
             (592, 270, 87, 21),
             (605, 259, 74, 14),
             (502, 280, 63, 13),
             (527, 272, 38, 11),
             (454, 229, 38, 11),
             (480, 232, 13, 45),
             (407, 229, 27, 10),
        )),
    }

    INITIAL = 'lines'

    def get_description(self):
        if self.scene.things['engine.superconductor'].get_data('working'):
            return "Power lines. They are delivering power to the engines."
        return "Power lines. It looks like they aren't working correctly."

    def is_interactive(self, tool=None):
        return False


class ArrowsTopLeft(Thing):
    NAME = 'engine.arrows_top_left'

    INTERACTS = {
        'arrows': InteractAnimated(25, 324, (
            'arrow_top_left_1.png', 'arrow_top_left_2.png',
            'arrow_top_left_3.png', 'arrow_top_left_4.png',
            ), 15,
        ),
    }

    INITIAL = 'arrows'

    def is_interactive(self, tool=None):
        return False


class ArrowsBottomLeft(Thing):
    NAME = 'engine.arrows_bottom_left'

    INTERACTS = {
        'arrows': InteractAnimated(32, 425, (
            'arrow_bottom_left_1.png', 'arrow_bottom_left_2.png',
            'arrow_bottom_left_3.png', 'arrow_bottom_left_4.png',
            ), 16,
        ),
    }

    INITIAL = 'arrows'

    def is_interactive(self, tool=None):
        return False


class ArrowsRight(Thing):
    NAME = 'engine.arrows_right'

    INTERACTS = {
        'arrows': InteractAnimated(708, 172, (
            'arrow_right_1.png', 'arrow_right_2.png',
            'arrow_right_3.png', 'arrow_right_4.png',
            ), 17,
        ),
    }

    INITIAL = 'arrows'

    def is_interactive(self, tool=None):
        return False


class DangerSign(Thing):
    NAME = 'engine.danger_sign'

    INTERACTS = {
        'sign': InteractAnimated(299, 341, (
            'danger_dim.png', 'danger_bright.png',
            ), 10,
        ),
    }

    INITIAL = 'sign'

    def is_interactive(self, tool=None):
        return False


class Stars(Thing):
    NAME = 'engine.stars'

    INTERACTS = {
        'stars': InteractAnimated(287, 455,
            ['stars_%d.png' % (i + 1) for i
             in range(5) + range(3, 0, -1)],
            30,
        ),
    }

    INITIAL = 'stars'

    def is_interactive(self, tool=None):
        return False

    def get_description(self):
        return "A gaping hole in the floor of the room. You're guessing" \
            " that's why there's a vacuum in here."


class CrackedPipe(Thing):
    NAME = "engine.cracked_pipe"

    INTERACTS = {
        'cracked': InteractImage(13, 402, 'cracked_pipe.png'),
        'taped': InteractImage(13, 402, 'duct_taped_pipe.png'),
    }

    INITIAL = 'cracked'

    INITIAL_DATA = {
        'fixed': False,
    }

    def get_description(self):
        if self.get_data('fixed'):
            return "The duct tape appears to be holding."
        else:
            return "The pipe looks cracked and won't hold" \
                   " fluid until it's fixed."

    def interact_with_duct_tape(self, item):
        if self.get_data('fixed'):
            return Result("The duct tape already there appears to be "
                          "sufficient.")
        else:
            self.set_data('fixed', True)
            self.set_interact('taped')
            return Result("You apply your trusty duct tape to the "
                          "creak, sealing it.")


class ComputerConsole(Thing):
    NAME = "engine.computer_console"

    INTERACTS = {
        'console': InteractRectUnion((
            (293, 287, 39, 36),
            (513, 330, 58, 50),
        )),
    }

    INITIAL = 'console'

    def interact_without(self):
        return Result(detail_view='engine_comp_detail')

    def get_description(self):
        return "A computer console. It's alarmingly close to the engine."


class EngineCompDetail(Scene):

    FOLDER = "engine"
    BACKGROUND = "engine_comp_detail.png"
    NAME = "engine_comp_detail"

    ALERTS = {
            'cryo leaking': 'ec_cryo_leaking.png',
            'cryo empty': 'ec_cryo_reservoir_empty.png',
            'super malfunction': 'ec_cryo_super_malfunction.png',
            }

    # Point to start drawing changeable alerts
    ALERT_OFFSET = (16, 100)
    ALERT_SPACING = 4

    def setup(self):
        self._alert_messages = {}
        for key, name in self.ALERTS.iteritems():
            self._alert_messages[key] = self.get_image(self.FOLDER, name)

    def _draw_alerts(self, surface):
        xpos, ypos = self.ALERT_OFFSET
        engine = self.game.scenes['engine']
        if not engine.things['engine.cracked_pipe'].get_data('fixed'):
            image = self._alert_messages['cryo leaking']
            surface.blit(image, (xpos, ypos))
            ypos += image.get_size()[1] + self.ALERT_SPACING
        if not engine.things['engine.cryo_containers'].get_data('filled'):
            image = self._alert_messages['cryo empty']
            surface.blit(image, (xpos, ypos))
            ypos += image.get_size()[1] + self.ALERT_SPACING
        if not engine.things['engine.superconductor'].get_data('working'):
            image = self._alert_messages['super malfunction']
            surface.blit(image, (xpos, ypos))
            ypos += image.get_size()[1] + self.ALERT_SPACING

    def draw_things(self, surface):
        self._draw_alerts(surface)
        super(EngineCompDetail, self).draw_things(surface)


class ToMap(Door):

    SCENE = "engine"

    INTERACTS = {
        "door": InteractNoImage(663, 360, 108, 193),
        }

    INITIAL = "door"

    def get_description(self):
        return "The airlock leads back to the rest of the ship."


SCENES = [Engine]
DETAIL_VIEWS = [EngineCompDetail]
