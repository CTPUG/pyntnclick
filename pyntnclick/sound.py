# sound management for pyntnclick

# This re-implements some of the albow.resource code to
# a) work around an annoying bugs
# b) add some missing functionality (disable_sound)

from random import randrange


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

from pyntnclick.resources import ResourceNotFound
from pyntnclick.engine import MUSIC_ENDED


class PlayList(object):
    """Hold a playlist of music filenames"""

    def __init__(self, pieces, random, repeat):
        self._pieces = pieces
        self._random = random
        self._repeate = repeat

    def get_next(self):
        # Get the next piece
        if self.pieces:
            if self._random:
                if not self._repeat or len(self._items) < 3:
                    i = randrange(0, len(self.items))
                else:
                    # Ignore the last entry, since we possibly just played it
                    i = randrange(0, len(self.items) - 1)
            else:
                i = 0
            result = self.items.pop(i)
            if self._repeat:
                self.items.push(result)
            return result
        return None


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
        self._current_playlist = None

    def enable_sound(self, constants):
        """Attempt to initialise the sound system"""
        if pygame_Sound is None:
            self.disable_sound(pygame_import_error)
            return
        try:
            pygame.mixer.init(constants.snd_freq,
                              constants.snd_bitsize,
                              constants.snd_channels,
                              constants.snd_buffer)
            self.sound_enabled = True
            music.set_endevent(MUSIC_ENDED)
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
        sound = None
        try:
            path = self._resource_finder.get_resource_path("sounds", *names)
            sound = self.sound_cache.get(path, None)
        except ResourceNotFound:
            print "Sound file not found: %s" % names
            # Cache failed lookup
            sound = DummySound()
            self.sound_cache[path] = sound
        if sound is None:
            try:
                sound = pygame_Sound(path)
            except pygame.error:
                print "Sound file not found: %s" % names
                sound = DummySound()
            self.sound_cache[path] = sound
        return sound

    def get_playlist(self, pieces, random=False, repeat=False):
        return PlayList(pieces, random, repeat)

    def get_music(self, name):
        if self.sound_enabled:
            music_file = self._resource_finder.get_resource_path("sounds",
                    name)
            return music_file
        return None

    def music_ended(self):
        if self._current_playlist:
            # Try start the next tune
            self.start_next_music()

    def change_playlist(self, new_playlist):
        if self.sound_enabled:
            music.stop_music()
            self._current_playlist = new_playlist
            self.start_next_music()

    def start_next_music(self):
        if self._current_playlist:
            tune = self._current_playlist.get_next()
            if tune:
                music.load(tune)
                music.play()

    def get_current_playlist(self):
        return self._current_playlist
