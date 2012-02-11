# Sound management for Suspended Sentence

# This re-implements some of the albow.resource code to
# a) work around an annoying bugs
# b) add some missing functionality (disable_sound)

import os

import pygame

try:
    from pygame.mixer import Sound as pygame_Sound
    from pygame.mixer import music
    pygame_import_error = None
except ImportError, e:
    # Save error, so we don't crash and can do the right thing later
    pygame_import_error = e
    pygame_Sound = None
    music = None

from pyntnclick.constants import FREQ, BITSIZE, CHANNELS, BUFFER
from pyntnclick.resources import ResourceNotFound

import albow.music


class DummySound(object):
    """A dummy sound object.

       This is a placeholder object with the same API as
       pygame.mixer.Sound which does nothing. Used when
       sounds are disabled so scense don't need to worry
       about the details.

       Inpsired by the same idea in Albow (by Greg Ewing)"""

    def play(self, *args):
        pass

    def stop(self):
        pass

    def get_length(self):
        return 0.0

    def get_num_channel(self):
        return 0

    def get_volume(self):
        return 0.0

    def fadeout(self, *args):
        pass


class Sound(object):
    """Global sound management and similiar useful things"""

    def __init__(self, resource_finder):
        self.sound_enabled = False
        self.sound_cache = {}
        self._resource_finder = resource_finder

    def enable_sound(self):
        """Attempt to initialise the sound system"""
        if pygame_Sound is None:
            self.disable_sound(pygame_import_error)
            return
        try:
            pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
            self.sound_enabled = True
        except pygame.error, exc:
            self.disable_sound(exc)

    def disable_sound(self, exc=None):
        """Disable the sound system"""
        self.sound_enabled = False
        if exc is not None:
            print 'Failed to initialise sound system'
            print 'Error: %s' % exc
            print 'Sound disabled'

    def get_sound(self, *names):
        if not self.sound_enabled:
            return DummySound()
        soundfile = os.path.join(names)
        sound = None
        try:
            path = self._resource_finder("sounds", soundfile)
            sound = self.sound_cache.get(path, None)
        except ResourceNotFound:
            print "Sound file not found: %s" % soundfile
            # Cache failed lookup
            sound = DummySound()
            self.sound_cache[path] = sound
        if sound is None:
            try:
                sound = pygame_Sound(path)
            except pygame.error:
                print "Sound file not found: %s" % soundfile
                sound = DummySound()
            self.sound_cache[path] = sound
        return sound

    def get_playlist(self, pieces, random=False, repeat=False):
        return albow.music.PlayList(pieces, random, repeat)

    def get_music(self, name, prefix):
        return albow.music.get_music(name, prefix=prefix)

    def change_playlist(self, new_playlist):
        albow.music.change_playlist(new_playlist)

    def get_current_playlist():
        if albow.music.music_enabled and albow.music.current_playlist:
            return albow.music.current_playlist


def start_next_music():
    """Start playing the next item from the current playlist immediately."""
    if albow.music.music_enabled and albow.music.current_playlist:
        next_music = albow.music.current_playlist.next()
        if next_music:
            #print "albow.music: loading", repr(next_music)
            music.load(next_music)
            music.play()
            albow.music.next_change_delay = albow.music.change_delay
        albow.music.current_music = next_music


# Monkey patch
albow.music.start_next_music = start_next_music
