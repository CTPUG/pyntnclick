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
    title = None
    short_name = 'pyntnclick'
    # Icon for the main window, in the icons basedir
    icon = None

    screen = (800, 600)
    snd_freq = 44100
    snd_bitsize = -16
    snd_channels = 2
    snd_buffer = 1024  # no. of samples

    button_size = 50
    scene_size = (screen[0], screen[1] - button_size)
    frame_rate = 25
    debug = _get_debug()

    font = 'DejaVuSans.ttf'
    bold_font = 'DejaVuSans-Bold.ttf'
    mono_font = 'DejaVuSans-Mono.ttf'
    font_size = 16
    text_color = 'black'
    label_padding = 10
    label_border = 3
    label_bg_color = (180, 180, 180, 220)
    label_border_color = (0, 0, 0, 0xFF)
    button_color = (0xFF, 0xFF, 0xFF, 0xFF)
    button_bg_color = (0x66, 0x66, 0x66, 0xFF)
    button_disabled_color = (0x66, 0x66, 0x66, 0xFF)

    modal_obscure_color = (0, 0, 0, 0xB0)
