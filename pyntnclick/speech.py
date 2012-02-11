# speech.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Speech playing and cache

import re

from sound import get_sound


# cache of string -> sound object mappings
_SPEECH_CACHE = {}

# characters not to allow in filenames
_REPLACE_RE = re.compile(r"[^a-z0-9-]+")


class SpeechError(RuntimeError):
    pass


def get_filename(key, text):
    """Simplify text to filename."""
    filename = "%s-%s" % (key, text)
    filename = filename.lower()
    filename = _REPLACE_RE.sub("_", filename)
    filename = filename[:30]
    filename = "%s.ogg" % filename
    return filename


def get_speech(thing_name, text):
    """Load a sound object from the cache."""
    key = (thing_name, text)
    if key in _SPEECH_CACHE:
        return _SPEECH_CACHE[key]
    filename = get_filename(thing_name, text)
    _SPEECH_CACHE[key] = sound = get_sound("speech", filename)
    return sound


def say(thing_name, text):
    """Play text as speech."""
    sound = get_speech(thing_name, text)
    sound.play()
