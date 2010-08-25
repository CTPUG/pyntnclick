# Sound management for Suspended Sentence

# This re-implements some of the albow.resource code to
# a) work around an annoying bugs
# b) add some missing functionality (disable_sound)

import os

import pygame
from pygame.mixer import music
from albow.resource import _resource_path, dummy_sound
import albow.music

sound_cache = {}

def get_sound(*names):
    if sound_cache is None:
        return dummy_sound
    path = _resource_path("sounds", names)
    sound = sound_cache.get(path)
    if not sound:
        if not os.path.isfile(path):
            missing_sound("File does not exist", path)
            return dummy_sound
        try:
            from pygame.mixer import Sound
        except ImportError, e:
            no_sound(e)
            return dummy_sound
        try:
            sound = Sound(path)
        except pygame.error, e:
            missing_sound(e, path)
            return dummy_sound
        sound_cache[path] = sound
    return sound


def no_sound(e):
    global sound_cache
    print "get_sound: %s" % e
    print "get_sound: Sound not available, continuing without it"
    sound_cache = None
    albow.music.music_enabled = False

def disable_sound():
    global sound_cache
    sound_cache = None
    albow.music.music_enabled = False

def missing_sound(e, name):
    print "albow.resource.get_sound: %s: %s" % (name, e)


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
