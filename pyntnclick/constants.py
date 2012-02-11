# Useful constants
# copyright boomslang team (see COPYRIGHT file for details)


class GameConstants(object):
    screen = (800, 600)
    snd_freq = 44100
    snd_bitsize = -16
    snd_channels = 2
    snd_buffer = 1024  # no. of samples

    button_size = 50
    scene_size = (screen[0], screen[1] - button_size)
    frame_rate = 25
    debug = False

    # User event IDs:
    enter = 1
    leave = 2
