# Useful constants
# copyright boomslang team (see COPYRIGHT file for details)

import os

DEBUG_ENVVAR = 'PYNTNCLICK_DEBUG'


def _get_debug():
    debug = os.getenv(DEBUG_ENVVAR, default=False)
    if debug in [False, 'False', '0']:
        return False
    return True


class GameConstants(object):
    screen = (800, 600)
    snd_freq = 44100
    snd_bitsize = -16
    snd_channels = 2
    snd_buffer = 1024  # no. of samples

    button_size = 50
    scene_size = (screen[0], screen[1] - button_size)
    frame_rate = 25
    debug = _get_debug()

    font = 'Vera.ttf'
    font_size = 16
    text_color = 'black'
    label_bg_color = (180, 180, 180, 180)

    # User event IDs:
    enter = 1
    leave = 2
