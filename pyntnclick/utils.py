# Misc utils I don't know where else to put

from __future__ import print_function, division

import sys

import pygame
from pygame.color import Color
from pygame.colordict import THECOLORS
from pygame.locals import SRCALPHA
from pygame.surface import Surface


if sys.version_info.major == 2:
    str_type = basestring
else:
    str_type = str


def list_scenes(scene_module, scene_list):
    """List the scenes in the state"""
    print("Available scenes and details:")
    for scene in scene_list:
        scenemod = __import__('%s.%s' % (scene_module, scene),
                         fromlist=[scene])
        if scenemod.SCENES:
            print(" * %s" % scene)
        else:
            print(" * %s (details only)" % scene)
        for detailcls in getattr(scenemod, 'DETAIL_VIEWS', []):
            print("   - %s" % detailcls.NAME)


def draw_rect_image(surface, color, rect, thickness):
    """Draw a rectangle with lines thickness wide"""
    # top
    surface.fill(color, (rect.left, rect.top, rect.width, thickness))
    # bottom
    surface.fill(color, (rect.left, rect.bottom - thickness, rect.width,
        thickness))
    # left
    surface.fill(color, (rect.left, rect.top, thickness, rect.height))
    # right
    surface.fill(color, (rect.right - thickness, rect.top, thickness,
        rect.height))


def convert_color(color):
    """Give me a pygame Color, dammit"""
    if isinstance(color, pygame.Color):
        return color
    if isinstance(color, str_type):
        return pygame.Color(color)
    return pygame.Color(*color)


def lookup_debug_color(number):
    """Choose a unique colour for this number, to aid debugging"""
    return Color(list(THECOLORS.keys())[number])

def render_text(text, fontname, font_size, color, bg_color, resource, size,
        centre=True):
    """Render the text so it will fit in the given size, reducing font
       size as needed.

       Note that this does not do any text wrapping."""
    done = False
    width, height = size
    color = convert_color(color)
    bg_color = convert_color(bg_color)
    surface = Surface(size, SRCALPHA).convert_alpha()
    surface.fill(bg_color)
    while not done and font_size > 0:
        # We bail at font_size 1 and just clip in that case, since we're
        # out of good options
        font = resource.get_font(fontname, font_size)
        text_surf = font.render(text, True, color)
        if (text_surf.get_width() > width or text_surf.get_height() > height):
            font_size -= 1
        else:
            done = True
    if centre:
        # Centre the text in the rect
        x = max(0, (width - text_surf.get_width()) // 2)
        y = max(0, (height - text_surf.get_height()) // 2)
    else:
        x = y = 0
    surface.blit(text_surf, (x, y))
    return surface


def make_reversible_list(seq):
    """Turns a list of images into a symmetric sequence that runs through
       the list first forward and then backwards.

       i.e. Given the sequence [a, b, c, d, e], it will return the sequence
       [a, b, c, d, e, d, c, b].
       This is intended as a helper for constructing looping animations."""
    return seq + seq[-2:0:-1]
