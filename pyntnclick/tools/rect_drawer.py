# Quickly hacked together helper for working out
# interactive regions in Suspended Sentence

from pygame.locals import (K_LEFT, K_RIGHT, K_UP, K_DOWN,
                           K_a, K_t, K_d, K_i, K_r, K_o, K_b, K_z,
                           QUIT, MOUSEBUTTONDOWN, MOUSEMOTION,
                           MOUSEBUTTONUP, KEYDOWN)
import pygame
import os

import pyntnclick.constants
from pyntnclick.widgets.text import LabelWidget, TextButton
from pyntnclick.widgets.base import Container, Button, TranslucentImage
from pyntnclick.widgets.filechooser import FileChooser
from pyntnclick.tools.utils import draw_rect_image


class RectDrawerError(Exception):
    """Raised when initilaization failed"""


class RectDrawerConstants(pyntnclick.constants.GameConstants):
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

    def __init__(self, rect, gd, colour, palette):
        super(ColourButton, self).__init__(rect, gd)
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

    def __init__(self, rect, gd, app_image):
        self.image = app_image
        super(AppPalette, self).__init__(rect, gd)
        self.selection = 0
        self.image.rect_color = pygame.color.Color(self.colors[self.selection])

        x = rect.left
        y = rect.top
        for num, col in enumerate(self.colors):
            if (x - rect.left + self.but_size) >= rect.width:
                x = rect.left
                y += self.but_size
            button = ColourButton(
                    pygame.Rect((x, y), (self.but_size, self.but_size)),
                    gd, col, self)
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
        super(AppImage, self).__init__(pygame.rect.Rect(0, 0,
            constants.screen[0], constants.screen[1]), gd)
        self.mode = 'draw'
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
        self.close_button = LabelWidget((0, 0), gd, 'Close')
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

    def find_existing_intersects(self):
        """Parse the things in the scene for overlaps"""
        scene = self._scene
        # Pylint hates this function
        for thing in scene.things.itervalues():
            for interact_name in thing.interacts:
                thing.set_interact(interact_name)
                if hasattr(thing.rect, 'collidepoint'):
                    thing_rects = [thing.rect]
                else:
                    thing_rects = thing.rect
                for thing2 in scene.things.itervalues():
                    if thing is thing2:
                        continue
                    for interact2_name in thing2.interacts:
                        thing2.set_interact(interact2_name)
                        if hasattr(thing2.rect, 'collidepoint'):
                            thing2_rects = [thing2.rect]
                        else:
                            thing2_rects = thing2.rect
                        for my_rect in thing_rects:
                            for other_rect in thing2_rects:
                                if my_rect.colliderect(other_rect):
                                    print 'Existing Intersecting rects'
                                    print ("  Thing1 %s Interact %s"
                                           % (thing.name, interact_name))
                                    print ("  Thing2 %s Interact %s"
                                           % (thing2.name, interact2_name))
                                    print "     Rects", my_rect, other_rect
        print

    def find_intersecting_rects(self, d):
        """Find if any rect collections intersect"""
        # I loath N^X brute search algorithm's, but whatever, hey
        scene = self._scene
        for (num, col) in enumerate(d):
            rect_list = d[col]
            for thing in scene.things.itervalues():
                for interact_name in thing.interacts:
                    thing.set_interact(interact_name)
                    if hasattr(thing.rect, 'collidepoint'):
                        thing_rects = [thing.rect]
                    else:
                        thing_rects = thing.rect
                    for other_rect in thing_rects:
                        for my_rect in rect_list:
                            if my_rect.colliderect(other_rect):
                                print 'Intersecting rects'
                                print "  Object %s" % num
                                print ("  Thing %s Interact %s"
                                       % (thing.name, interact_name))
                                print "     Rects", my_rect, other_rect
                if thing.INITIAL:
                    thing.set_interact(thing.INITIAL)
            print
            for (num2, col2) in enumerate(d):
                if num2 == num:
                    continue
                other_list = d[col2]
                for my_rect in rect_list:
                    for other_rect in other_list:
                        if my_rect.colliderect(other_rect):
                            print 'Intersecting rects',
                            print '  Object %s and %s' % (num, num2)
                            print "     Rects", my_rect, other_rect
            print
            print

    def toggle_things(self, ev, widget):
        self.draw_things = not self.draw_things

    def toggle_thing_rects(self, ev, widget):
        self.draw_thing_rects = not self.draw_thing_rects
        scene = self._scene
        for thing in scene.things.itervalues():
            if not self.draw_thing_rects:
                if not hasattr(thing, 'old_colour'):
                    thing.old_colour = thing._interact_hilight_color
                thing._interact_hilight_color = None
            else:
                thing._interact_hilight_color = thing.old_colour

    def toggle_images(self, ev, widget):
        self.draw_images = not self.draw_images
        for image in self.images:
            image.visible = self.draw_images
        if self.current_image:
            self.current_image.visible = self.draw_images
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
        self.mode = 'draw'

    def del_mode(self, ev, widget):
        self.mode = 'del'
        self.start_pos = None
        self.end_pos = None

    def invalidate(self):
        self.clear_display = True

    def draw(self, surface):
        self.do_prepare()
        if self.clear_display:
            surface.fill(pygame.color.Color(0, 0, 0))
            self.clear_display = False

        if self.zoom_display:
            base_surface = surface.copy()
            self.do_unzoomed_draw(base_surface)
            zoomed = pygame.transform.scale(base_surface,
                            (constants.zoom * base_surface.get_width(),
                             constants.zoom * base_surface.get_height()))
            area = pygame.rect.Rect(self.zoom_offset[0], self.zoom_offset[1],
                                    self.zoom_offset[0] + constants.screen[0],
                                    self.zoom_offset[1] + constants.screen[1])
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
        if self.mode == 'draw' and self.start_pos and self.draw_rects:
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
        if self.current_image and self.mode == 'image':
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
            print 'Rect %d : ' % num
            for rect in d[col]:
                r = rect.move(self.offset)
                print '   (%d, %d, %d, %d),' % (r.x, r.y, r.w, r.h)
            print
        for i, image in enumerate(self.images):
            print 'Image %d' % i
            rect = image.rect
            r = rect.move(self.offset)
            print '   (%d, %d, %d, %d),' % (r.x, r.y, r.w, r.h)
            print
        print

    def image_load(self, ev, widget):
        if self.filechooser is None:
            self.filechooser = FileChooser((0, 0), self.gd, os.curdir,
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
        except pygame.error, e:
            print 'Unable to load image %s (reason %s)' % (filename, e)

    def image_mode(self, ev, widget):
        self.mode = 'image'
        self.start_pos = None
        self.end_pos = None
        # So we do the right thing for off screen images
        self.old_mouse_pos = None

    def cycle_mode(self, ev, widget):
        self.mode = 'cycle'

    def _conv_pos(self, mouse_pos):
        if self.zoom_display:
            pos = ((mouse_pos[0] + self.zoom_offset[0]) / constants.zoom,
                   (mouse_pos[1] + self.zoom_offset[1]) / constants.zoom)
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
        offset = [zoom_pos[0] - constants.screen[0] / 2,
                zoom_pos[1] - constants.screen[1] / 2]
        self._check_limits(offset)
        self.zoom_offset = tuple(offset)

    def _move_zoom(self, x, y):
        offset = list(self.zoom_offset)
        offset[0] += constants.zoom_step * x
        offset[1] += constants.zoom_step * y
        self._check_limits(offset)
        self.zoom_offset = tuple(offset)

    def key_down(self, ev, widget):
        if self.mode == 'image' and self.current_image:
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
        if self.mode == 'del':
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
        elif self.mode == 'cycle':
            scene = self._scene
            cand = None
            for thing in scene.things.itervalues():
                if thing.contains(pos):
                    cand = thing
                    break
            if cand:
                # Find current interacts in this thing
                cur_interact = cand.current_interact
                j = cand.interacts.values().index(cur_interact)
                if j + 1 < len(cand.interacts):
                    next_name = cand.interacts.keys()[j + 1]
                else:
                    next_name = cand.interacts.keys()[0]
                if cand.interacts[next_name] != cur_interact:
                    cand.set_interact(next_name)
        elif self.mode == 'draw':
            self.start_pos = pos
            self.end_pos = pos
        elif self.mode == 'image':
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
        if self.mode == 'draw':
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
        if self.mode == 'image' and self.current_image:
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
        elif ev.buttons[0] == 1 and self.mode == 'draw':
            self.end_pos = self._conv_pos(ev.pos)
            return True
        return False

    def animate(self):
        if self.draw_anim:
            self._scene.animate()


class ModeLabel(LabelWidget):

    def __init__(self, rect, gd, app_image):
        self.app_image = app_image
        super(ModeLabel, self).__init__(rect,
                gd, 'Mode : ', fontname=constants.bold_font,
                fontsize=15, color=pygame.color.Color(128, 0, 255))

    def draw(self, surface):
        self.do_prepare()
        text = 'Mode : %s' % self.app_image.mode
        if self.text != text:
            self.text = text
            self.prepare()
        super(ModeLabel, self).draw(surface)


def make_button(text, gd, action, ypos):
    rect = pygame.rect.Rect(0, 0, constants.menu_width,
            constants.menu_button_height)
    rect.move_ip(805, ypos)
    button = TextButton(rect, gd, text, fontname=constants.font, fontsize=12,
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
            raise RectDrawerError('Invalid scene: %s' % gd._initial_scene)
        gd.sound.disable_sound()  # No sound here

        if detail:
            try:
                scene = state.detail_views[detail]
            except KeyError:
                raise RectDrawerError('Invalid detail: %s' % detail)

        self.paused = False

        self.image = AppImage(self, gd, state, scene, detail is not None)
        self.add(self.image)
        mode_label = ModeLabel(pygame.Rect((805, 0), (200, 25)),
                self.gd, self.image)
        self.add(mode_label)
        y = mode_label.rect.height
        draw = make_button('Draw Rect', gd, self.image.draw_mode, y)
        self.add(draw)
        y += draw.rect.height
        load_image = make_button("Load image", gd, self.image.image_load, y)
        self.add(load_image)
        y += load_image.rect.height
        add_image = make_button("Place/Move images", gd,
                self.image.image_mode, y)
        add_image.enabled = False
        self.add(add_image)
        self.image.place_image_menu = add_image
        y += add_image.rect.height
        cycle = make_button("Cycle interacts", gd, self.image.cycle_mode, y)
        self.add(cycle)
        y += cycle.rect.height
        delete = make_button("Delete Objects", gd, self.image.del_mode, y)
        self.add(delete)
        y += delete.rect.height
        palette = AppPalette(pygame.Rect((810, y), (200, 0)), gd, self.image)
        self.add(palette)
        y += palette.rect.height
        print_rects = make_button("Print objects", gd,
                self.image.print_objs, y)
        self.add(print_rects)
        y += print_rects.rect.height
        toggle_things = make_button("Show Things (t)", gd,
                self.image.toggle_things, y)
        self.add(toggle_things)
        y += toggle_things.rect.height
        toggle_thing_rects = make_button("Show Thing Rects (r)", gd,
                self.image.toggle_thing_rects, y)
        self.add(toggle_thing_rects)
        y += toggle_thing_rects.rect.height
        toggle_images = make_button("Show Images (i)", gd,
                self.image.toggle_images, y)
        self.add(toggle_images)
        y += toggle_images.rect.height
        trans_images = make_button("Opaque Images (o)", gd,
                self.image.toggle_trans_images, y)
        self.add(trans_images)
        y += trans_images.rect.height
        toggle_rects = make_button("Show Drawn Rects (d)", gd,
                self.image.toggle_rects, y)
        self.add(toggle_rects)
        y += toggle_rects.rect.height
        toggle_toolbar = make_button("Show Toolbar (b)", gd,
                self.image.toggle_toolbar, y)
        self.add(toggle_toolbar)
        y += toggle_toolbar.rect.height
        toggle_anim = make_button("Show Animations (a)", gd,
                self.image.toggle_anim, y)
        self.add(toggle_anim)
        y += toggle_anim.rect.height
        toggle_zoom = make_button("Zoom (z)", gd, self.image.toggle_zoom, y)
        self.add(toggle_zoom)
        y += toggle_zoom.rect.height
        quit_but = make_button("Quit", gd, self.quit, 570)
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
        self.app = RectApp(rect, self._gd, detail)

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
