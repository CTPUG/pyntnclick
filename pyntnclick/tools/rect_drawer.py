# Quickly hacked together helper for working out
# interactive regions in Suspended Sentence

from __future__ import print_function, division

from pygame.locals import (K_LEFT, K_RIGHT, K_UP, K_DOWN,
                           K_a, K_t, K_d, K_i, K_r, K_o, K_b, K_z,
                           QUIT, MOUSEBUTTONDOWN, MOUSEMOTION,
                           MOUSEBUTTONUP, KEYDOWN)
import pygame
import os

from .. import constants
from ..i18n import _
from ..utils import draw_rect_image

from ..widgets.text import LabelWidget, TextButton
from ..widgets.base import Container, Button, TranslucentImage
from ..widgets.filechooser import FileChooser

DRAW, CYCLE, DELETE, IMAGE = range(4)


class RectDrawerError(Exception):
    """Raised when initilaization failed"""


class RectDrawerConstants(constants.GameConstants):
    debug = True
    menu_width = 200
    menu_button_height = 25
    zoom = 4
    zoom_step = 100

constants = RectDrawerConstants()


class ColourButton(Button):
    """Button for selecting a colour"""

    sel_colour = pygame.color.Color(255, 255, 255)
    unsel_colour = pygame.color.Color(128, 128, 128)

    padding = 2
    border = 3

    def __init__(self, rect, gd, colour, palette, size=None):
        super(ColourButton, self).__init__(rect, gd, size=size)
        self._colour = pygame.color.Color(colour)
        self._button_rect = self.rect.inflate(-self.padding, -self.padding)
        self._colour_rect = self._button_rect.inflate(-self.border,
                -self.border)
        self.selected = False
        self._palette = palette
        self.add_callback('clicked', self.fix_selection)

    def fix_selection(self, ev, widget):
        self._palette.cur_selection.selected = False
        self.selected = True
        self._palette.cur_selection = self

    def draw(self, surface):
        if self.visible:
            self.do_prepare()
            surface.fill(pygame.color.Color(0, 0, 0), self.rect)
            if self.selected:
                surface.fill(self.sel_colour, self._button_rect)
            else:
                surface.fill(self.unsel_colour, self._button_rect)
            surface.fill(self._colour, self._colour_rect)


class AppPalette(Container):

    but_size = 35

    colors = [
            'red', 'maroon1', 'palevioletred1', 'moccasin', 'orange',
            'honeydew', 'yellow', 'gold', 'goldenrod', 'brown',
            'blue', 'purple', 'darkorchid4', 'thistle', 'skyblue1',
            'green', 'palegreen1', 'darkgreen', 'aquamarine', 'darkolivegreen',
            ]

    def __init__(self, pos, gd, app_image, size=None):
        self.image = app_image
        super(AppPalette, self).__init__(pos, gd, size=size)
        self.selection = 0
        self.image.rect_color = pygame.color.Color(self.colors[self.selection])

        x, y = pos
        for num, col in enumerate(self.colors):
            if (x - self.rect.left + self.but_size) >= self.rect.width:
                x = self.rect.left
                y += self.but_size
            button = ColourButton((x, y),
                    gd, col, self, size=(self.but_size, self.but_size))
            x += self.but_size
            if num == 0:
                self.cur_selection = button
                button.fix_selection(None, None)
            button.add_callback('clicked', self.click_item, num)
            self.add(button)
        # Fix height
        self.rect.height = y + self.but_size - self.rect.top

    def click_item(self, ev, widget, number):
        self.selection = number
        self.image.rect_color = pygame.color.Color(self.colors[number])


class AppImage(Container):

    rect_thick = 3
    draw_thick = 1

    def __init__(self, parent, gd, state, scene, detail):
        self.state = state
        super(AppImage, self).__init__((0, 0), gd, size=constants.screen)
        self.mode = DRAW
        self._scene = scene
        self._parent = parent
        self._detail = detail
        self.rects = []
        self.images = []
        self.start_pos = None
        self.end_pos = None
        self.rect_color = pygame.color.Color('white')
        self.current_image = None
        self.place_image_menu = None
        self.close_button = LabelWidget((0, 0), gd, _('Close'))
        self.close_button.fg_color = (0, 0, 0)
        self.close_button.bg_color = (0, 0, 0)
        self.draw_rects = True
        self.draw_things = True
        self.draw_thing_rects = True
        self.draw_images = True
        self.trans_images = False
        self.draw_toolbar = True
        self.old_mouse_pos = None
        self.zoom_display = False
        self.draw_anim = False
        self.zoom_offset = (600, 600)
        self.clear_display = False
        self.filechooser = None
        if self._detail:
            w, h = self._scene.get_detail_size()
            rect = pygame.rect.Rect(0, 0, w, h)
            self.close_button.rect.midbottom = rect.midbottom
            self.offset = (0, 0)
        else:
            self.offset = (-self._scene.OFFSET[0],
                           -self._scene.OFFSET[1])
        self.find_existing_intersects()
        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.add_callback(MOUSEBUTTONUP, self.mouse_up)
        self.add_callback(MOUSEMOTION, self.mouse_move)
        self.add_callback(KEYDOWN, self.key_down)

    def get_mode_name(self):
        """Return the translated mode name"""
        # We do things this way to avoid defining translated strings
        # at import time
        if self.mode == DRAW:
            return _("draw")
        elif self.mode == CYCLE:
            return _("cycle")
        elif self.mode == DELETE:
            return _("delete")
        elif self.mode == IMAGE:
            return _("image")
        else:
            raise RuntimeError("Invalid mode")

    def _print_thing(self, thing, interact_name):
        """Helper to avoid repeated translations"""
        print(_("Thing %(thing)s Interact %(interact)s") %
               {'thing': thing.name, 'interact': interact_name})

    def _print_rects(self, rect1, rect2):
        """Helper to avoid repeated translations"""
        print(_("     Rects"), rect1, rect2)

    def find_existing_intersects(self):
        """Parse the things in the scene for overlaps"""
        scene = self._scene
        # Pylint hates this function
        for thing in scene.things.values():
            for interact_name in thing.interacts:
                thing._set_interact(interact_name)
                if hasattr(thing.rect, 'collidepoint'):
                    thing_rects = [thing.rect]
                else:
                    thing_rects = thing.rect
                for thing2 in scene.things.values():
                    if thing is thing2:
                        continue
                    for interact2_name in thing2.interacts:
                        thing2._set_interact(interact2_name)
                        if hasattr(thing2.rect, 'collidepoint'):
                            thing2_rects = [thing2.rect]
                        else:
                            thing2_rects = thing2.rect
                        for my_rect in thing_rects:
                            for other_rect in thing2_rects:
                                if my_rect.colliderect(other_rect):
                                    print(_('Existing Intersecting rects'))
                                    self._print_thing(thing, interact_name)
                                    self._print_thing(thing2, interact2_name)
                                    self._print_rects(my_rect, other_rect)
        print

    def find_intersecting_rects(self, d):
        """Find if any rect collections intersect"""
        # I loath N^X brute search algorithms, but whatever, hey
        scene = self._scene
        for (num, col) in enumerate(d):
            rect_list = d[col]
            for thing in scene.things.values():
                for interact_name in thing.interacts:
                    thing._set_interact(interact_name)
                    if hasattr(thing.rect, 'collidepoint'):
                        thing_rects = [thing.rect]
                    else:
                        thing_rects = thing.rect
                    for other_rect in thing_rects:
                        for my_rect in rect_list:
                            if my_rect.colliderect(other_rect):
                                print(_('Intersecting rects'))
                                print(_("  Object %s") % num)
                                self._print_thing(thing, interact_name)
                                self._print_rects(my_rect, other_rect)
                if thing.INITIAL:
                    thing._set_interact(thing.INITIAL)
            print
            for (num2, col2) in enumerate(d):
                if num2 == num:
                    continue
                other_list = d[col2]
                for my_rect in rect_list:
                    for other_rect in other_list:
                        if my_rect.colliderect(other_rect):
                            print(_('Intersecting rects'))
                            print(_('  Object %(object1)s and %(object2)s') %
                                  {'object1': num, 'object2': num2})
                            self._print_rects(my_rect, other_rect)
            print
            print

    def toggle_things(self, ev, widget):
        self.draw_things = not self.draw_things

    def toggle_thing_rects(self, ev, widget):
        self.draw_thing_rects = not self.draw_thing_rects
        scene = self._scene
        for thing in scene.things.values():
            if not self.draw_thing_rects:
                if not hasattr(thing, 'old_colour'):
                    thing.old_colour = thing._interact_hilight_color
                thing._interact_hilight_color = None
            else:
                thing._interact_hilight_color = thing.old_colour

    def toggle_images(self, ev, widget):
        self.draw_images = not self.draw_images
        for image in self.images:
            image.set_visible(self.draw_images)
        if self.current_image:
            self.current_image.set_visible(self.draw_images)
        self.invalidate()

    def toggle_trans_images(self, ev, widget):
        self.trans_images = not self.trans_images
        for image in self.images:
            image.translucent = self.trans_images
        if self.current_image:
            self.current_image.translucent = self.trans_images
        self.invalidate()

    def toggle_rects(self, ev, widget):
        self.draw_rects = not self.draw_rects

    def toggle_toolbar(self, ev, widget):
        self.draw_toolbar = not self.draw_toolbar

    def toggle_zoom(self, ev, widget):
        self.zoom_display = not self.zoom_display
        self.invalidate()

    def toggle_anim(self, ev, widget):
        self.draw_anim = not self.draw_anim

    def draw_mode(self, ev, widget):
        self.mode = DRAW

    def del_mode(self, ev, widget):
        self.mode = DELETE
        self.start_pos = None
        self.end_pos = None

    def invalidate(self):
        self.clear_display = True

    def draw(self, surface):
        if not self.visible:
            return
        self.do_prepare()
        if self.clear_display:
            surface.fill(pygame.color.Color(0, 0, 0),
                    pygame.Rect(0, 0, constants.screen[0],
                        constants.screen[1]))
            self.clear_display = False

        if self.zoom_display:
            base_surface = surface.copy()
            self.do_unzoomed_draw(base_surface)
            zoomed = pygame.transform.scale(base_surface,
                            (constants.zoom * base_surface.get_width(),
                             constants.zoom * base_surface.get_height()))
            area = pygame.rect.Rect(self.zoom_offset[0], self.zoom_offset[1],
                                    constants.screen[0], constants.screen[1])
            surface.blit(zoomed, (0, 0), area)
        else:
            self.do_unzoomed_draw(surface)

    def do_unzoomed_draw(self, surface):
        if self.draw_things:
            self._scene.draw(surface)
        else:
            self._scene.draw_background(surface)
        if self._detail:
            # We duplicate draw logic here, so we zoom the close
            # button correctly
            self.close_button.draw(surface)
        if self.mode == DRAW and self.start_pos and self.draw_rects:
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            rect.normalize()
            draw_rect_image(surface, self.rect_color, rect, self.draw_thick)
        if self.draw_rects:
            for (col, rect) in self.rects:
                draw_rect_image(surface, col, rect, self.rect_thick)
        for image in self.images:
            image.draw(surface)
        if self.current_image and self.mode == IMAGE:
            self.current_image.draw(surface)
        if self.draw_toolbar:
            tb_surf = surface.subsurface(0, constants.screen[1]
                                            - constants.button_size,
                                         constants.screen[0],
                                         constants.button_size).convert_alpha()
            tb_surf.fill(pygame.color.Color(127, 0, 0, 191))
            surface.blit(tb_surf, (0, constants.screen[1]
                                      - constants.button_size))

    def _make_dict(self):
        d = {}
        for col, rect in self.rects:
            col = (col.r, col.g, col.b)
            d.setdefault(col, [])
            d[col].append(rect)
        return d

    def print_objs(self, ev, widget):
        d = self._make_dict()
        self.find_intersecting_rects(d)
        for (num, col) in enumerate(d):
            print(_('Rect %d : ') % num)
            for rect in d[col]:
                r = rect.move(self.offset)
                print('   (%d, %d, %d, %d),' % (r.x, r.y, r.w, r.h))
            print()
        for i, image in enumerate(self.images):
            print(_('Image %d') % i)
            rect = image.rect
            r = rect.move(self.offset)
            print('   (%d, %d, %d, %d),' % (r.x, r.y, r.w, r.h))
            print()
        print()

    def image_load(self, ev, widget):
        if self.filechooser is None:
            self.filechooser = FileChooser((0, 0), self.gd, None, os.curdir,
                    self.do_load_image)
        else:
            self.filechooser.refresh()
        self.invalidate()
        self._parent.paused = True
        self._parent.add(self.filechooser)

    def do_load_image(self, filename):
        try:
            self.current_image = TranslucentImage((0, 0), self.gd,
                    pygame.image.load(filename))
            if not self.draw_images:
                # Selecting an image makes image visible
                self.toggle_images(None, None)
            self.current_image.translucent = self.trans_images
            self.place_image_menu.enabled = True
            self.current_image.rect = self.current_image.rect.move(
                    constants.screen[0] + constants.menu_width,
                    constants.screen[1])
            self.image_mode(None, None)
        except pygame.error as e:
            print('Unable to load image %s (reason %s)' % (filename, e))

    def image_mode(self, ev, widget):
        self.mode = IMAGE
        self.start_pos = None
        self.end_pos = None
        # So we do the right thing for off screen images
        self.old_mouse_pos = None

    def cycle_mode(self, ev, widget):
        self.mode = CYCLE

    def _conv_pos(self, mouse_pos):
        if self.zoom_display:
            pos = ((mouse_pos[0] + self.zoom_offset[0]) // constants.zoom,
                   (mouse_pos[1] + self.zoom_offset[1]) // constants.zoom)
        else:
            pos = mouse_pos
        return pos

    def _check_limits(self, offset):
        if offset[0] < 0:
            offset[0] = 0
        if offset[1] < 0:
            offset[1] = 0
        width, height = constants.screen
        if offset[0] > constants.zoom * width - width:
            offset[0] = constants.zoom * width - width
        if offset[1] > constants.zoom * height - height:
            offset[1] = constants.zoom * height - height

    def _make_zoom_offset(self, pos):
        zoom_pos = (pos[0] * constants.zoom, pos[1] * constants.zoom)
        offset = [zoom_pos[0] - constants.screen[0] // 2,
                zoom_pos[1] - constants.screen[1] // 2]
        self._check_limits(offset)
        self.zoom_offset = tuple(offset)

    def _move_zoom(self, x, y):
        offset = list(self.zoom_offset)
        offset[0] += constants.zoom_step * x
        offset[1] += constants.zoom_step * y
        self._check_limits(offset)
        self.zoom_offset = tuple(offset)

    def key_down(self, ev, widget):
        if self.mode == IMAGE and self.current_image:
            # Move the image by 1 pixel
            cur_pos = self.current_image.rect.center
            if ev.key == K_LEFT:
                self.current_image.rect.center = (cur_pos[0] - 1, cur_pos[1])
            elif ev.key == K_RIGHT:
                self.current_image.rect.center = (cur_pos[0] + 1, cur_pos[1])
            elif ev.key == K_UP:
                self.current_image.rect.center = (cur_pos[0], cur_pos[1] - 1)
            elif ev.key == K_DOWN:
                self.current_image.rect.center = (cur_pos[0], cur_pos[1] + 1)
        elif self.zoom_display:
            if ev.key == K_LEFT:
                self._move_zoom(-1, 0)
            elif ev.key == K_RIGHT:
                self._move_zoom(1, 0)
            elif ev.key == K_UP:
                self._move_zoom(0, -1)
            elif ev.key == K_DOWN:
                self._move_zoom(0, 1)

        if ev.key == K_o:
            self.toggle_trans_images(None, None)
        elif ev.key == K_t:
            self.toggle_things(None, None)
        elif ev.key == K_r:
            self.toggle_thing_rects(None, None)
        elif ev.key == K_i:
            self.toggle_images(None, None)
        elif ev.key == K_d:
            self.toggle_rects(None, None)
        elif ev.key == K_b:
            self.toggle_toolbar(None, None)
        elif ev.key == K_z:
            self.toggle_zoom(None, None)
        elif ev.key == K_a:
            self.toggle_anim(None, None)

    def mouse_down(self, ev, widget):
        pos = self._conv_pos(ev.pos)
        if self._parent.paused:
            # Ignore this if the filechooser is active
            return False
        if self.mode == DELETE:
            cand = None
            # Images are drawn above rectangles, so search those first
            for image in self.images:
                if image.rect.collidepoint(pos):
                    cand = image
                    break
            if cand:
                self.images.remove(cand)
                self.invalidate()
                return
            for (col, rect) in self.rects:
                if rect.collidepoint(pos):
                    cand = (col, rect)
                    break
            if cand:
                self.rects.remove(cand)
                self.invalidate()
        elif self.mode == CYCLE:
            scene = self._scene
            cand = None
            for thing in scene.things.values():
                if thing.contains(pos):
                    cand = thing
                    break
            if cand:
                # Find current interacts in this thing
                cur_interact = cand.current_interact
                values = list(cand.interacts.values())
                keys = list(cand.interacts.keys())
                j = values.index(cur_interact)
                if j + 1 < len(keys):
                    next_name = keys[j + 1]
                else:
                    next_name = keys[0]
                if cand.interacts[next_name] != cur_interact:
                    cand._set_interact(next_name)
        elif self.mode == DRAW:
            self.start_pos = pos
            self.end_pos = pos
        elif self.mode == IMAGE:
            if self.current_image:
                self.images.append(self.current_image)
                self.current_image = None
                self.old_mouse_pos = None
                self.invalidate()
            else:
                cand = None
                for image in self.images:
                    if image.rect.collidepoint(pos):
                        cand = image
                        break
                if cand:
                    self.images.remove(cand)
                    self.current_image = cand
                    # We want to move relative to the current mouse pos, so
                    self.old_mouse_pos = pos
                    self.invalidate()

    def mouse_up(self, ev, widget):
        if self._parent.paused:
            return False
        if self.mode == DRAW:
            if self.start_pos is None:
                # We've come here not via a drawing situation, so bail
                return False
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            rect.normalize()
            self.rects.append((self.rect_color, rect))
            self.start_pos = self.end_pos = None

    def mouse_move(self, ev, widget):
        # We're only interested in this if left mouse button is down or we've
        # got and image
        if self.mode == IMAGE and self.current_image:
            pos = self._conv_pos(ev.pos)
            if self.old_mouse_pos:
                delta = (pos[0] - self.old_mouse_pos[0],
                         pos[1] - self.old_mouse_pos[1])
                self.current_image.rect.center = (
                        self.current_image.rect.center[0] + delta[0],
                        self.current_image.rect.center[1] + delta[1])
            else:
                self.current_image.rect.center = pos
            self.invalidate()
            self.old_mouse_pos = pos
            return True
        elif ev.buttons[0] == 1 and self.mode == DRAW:
            self.end_pos = self._conv_pos(ev.pos)
            return True
        return False

    def animate(self):
        if self.draw_anim:
            self._scene.animate()


class ModeLabel(LabelWidget):

    def __init__(self, pos, gd, app_image, size=None):
        self.app_image = app_image
        super(ModeLabel, self).__init__(pos,
                gd, _('Mode : '), fontname=constants.bold_font,
                fontsize=15, color=pygame.color.Color(128, 0, 255),
                size=size)
        self.start_rect = self.rect.copy()

    def draw(self, surface):
        self.do_prepare()
        text = _('Mode : %s') % self.app_image.get_mode_name()
        if self.text != text:
            self.text = text
            self.is_prepared = False
            self.rect = self.start_rect.copy()
            self.do_prepare()
        super(ModeLabel, self).draw(surface)


def make_button(text, gd, action, ypos):
    rect = pygame.rect.Rect(0, 0, constants.menu_width,
            constants.menu_button_height)
    rect.move_ip(805, ypos)
    button = TextButton(rect.topleft, gd, text, size=(constants.menu_width,
        constants.menu_button_height),
            fontname=constants.font, fontsize=12,
            color=pygame.color.Color(255, 255, 0), border=1, padding=3)
    button.add_callback('clicked', action)
    return button


class RectApp(Container):
    """The actual rect drawer main app"""
    def __init__(self, rect, gd, detail):
        super(RectApp, self).__init__(rect, gd)

        try:
            state = gd.initial_state()
            scene = state.scenes[gd._initial_scene]
        except KeyError:
            raise RectDrawerError(_('Invalid scene: %s') % gd._initial_scene)
        gd.sound.disable_sound()  # No sound here

        if detail:
            try:
                scene = state.detail_views[detail]
            except KeyError:
                raise RectDrawerError(_('Invalid detail: %s') % detail)

        self.paused = False

        self.image = AppImage(self, gd, state, scene, detail is not None)
        self.add(self.image)
        mode_label = ModeLabel((805, 0), self.gd, self.image, size=(200, 50))
        self.add(mode_label)
        y = mode_label.rect.height
        draw = make_button(_('Draw Rect'), gd, self.image.draw_mode, y)
        self.add(draw)
        y += draw.rect.height
        load_image = make_button(_("Load image"), gd, self.image.image_load, y)
        self.add(load_image)
        y += load_image.rect.height
        add_image = make_button(_("Place/Move images"), gd,
                self.image.image_mode, y)
        add_image.enabled = False
        self.add(add_image)
        self.image.place_image_menu = add_image
        y += add_image.rect.height
        cycle = make_button(_("Cycle interacts"), gd, self.image.cycle_mode, y)
        self.add(cycle)
        y += cycle.rect.height
        delete = make_button(_("Delete Objects"), gd, self.image.del_mode, y)
        self.add(delete)
        y += delete.rect.height
        palette = AppPalette((810, y), gd, self.image, size=(200, 0))
        self.add(palette)
        y += palette.rect.height
        print_rects = make_button(_("Print objects"), gd,
                self.image.print_objs, y)
        self.add(print_rects)
        y += print_rects.rect.height
        toggle_things = make_button(_("Show Things (t)"), gd,
                self.image.toggle_things, y)
        self.add(toggle_things)
        y += toggle_things.rect.height
        toggle_thing_rects = make_button(_("Show Thing Rects (r)"), gd,
                self.image.toggle_thing_rects, y)
        self.add(toggle_thing_rects)
        y += toggle_thing_rects.rect.height
        toggle_images = make_button(_("Show Images (i)"), gd,
                self.image.toggle_images, y)
        self.add(toggle_images)
        y += toggle_images.rect.height
        trans_images = make_button(_("Opaque Images (o)"), gd,
                self.image.toggle_trans_images, y)
        self.add(trans_images)
        y += trans_images.rect.height
        toggle_rects = make_button(_("Show Drawn Rects (d)"), gd,
                self.image.toggle_rects, y)
        self.add(toggle_rects)
        y += toggle_rects.rect.height
        toggle_toolbar = make_button(_("Show Toolbar (b)"), gd,
                self.image.toggle_toolbar, y)
        self.add(toggle_toolbar)
        y += toggle_toolbar.rect.height
        toggle_anim = make_button(_("Show Animations (a)"), gd,
                self.image.toggle_anim, y)
        self.add(toggle_anim)
        y += toggle_anim.rect.height
        toggle_zoom = make_button(_("Zoom (z)"), gd,
                self.image.toggle_zoom, y)
        self.add(toggle_zoom)
        y += toggle_zoom.rect.height
        quit_but = make_button(_("Quit"), gd, self.quit, 570)
        self.add(quit_but)

    def quit(self, ev, widget):
        pygame.event.post(pygame.event.Event(QUIT))

    def animate(self):
        self.image.animate()


class RectEngine(object):
    """Engine for the rect drawer."""

    def __init__(self, gd, detail):
        self.state = None
        self._gd = gd
        rect = pygame.display.get_surface().get_rect()
        self.app = RectApp(rect.topleft, self._gd, detail)

    def run(self):
        """App loop"""
        clock = pygame.time.Clock()
        while True:
            events = pygame.event.get()
            for ev in events:
                if ev.type == QUIT:
                    return
                else:
                    self.app.event(ev)
            self.app.animate()
            surface = pygame.display.get_surface()
            self.app.draw(surface)
            pygame.display.flip()
            clock.tick(self._gd.constants.frame_rate)


def make_rect_display():
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((constants.screen[0]
        + constants.menu_width, constants.screen[1]))
