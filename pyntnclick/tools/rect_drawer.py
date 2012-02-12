# Quickly hacked together helper for working out
# interactive regions in Suspended Sentence

# XXX: Threw away albow
#from albow.root import RootWidget
#from albow.utils import frame_rect
#from albow.widget import Widget
#from albow.controls import Button, Image
#from albow.palette_view import PaletteView
#from albow.file_dialogs import request_old_filename
#from albow.resource import get_font
RootWidget = object
frame_rect = None
Widget = object
Button = object
Image = object
PaletteView = object
request_old_filename = None
get_font = None

from pygame.locals import (K_LEFT, K_RIGHT, K_UP, K_DOWN,
                           K_a, K_t, K_d, K_i, K_r, K_o, K_b, K_z,
                           BLEND_RGBA_MIN, SRCALPHA, QUIT)
import pygame

import pyntnclick.constants
from pyntnclick import state
state.DEBUG_RECTS = True
from pyntnclick.widgets import BoomLabel
from pyntnclick.widgets.base import Container


class RectDrawerConstants(pyntnclick.constants.GameConstants):
    debug = True
    menu_width = 200
    menu_button_height = 25
    zoom = 4
    zoom_step = 100

constants = RectDrawerConstants()


class AppPalette(PaletteView):

    sel_width = 5

    colors = [
            'red', 'maroon1', 'palevioletred1', 'moccasin', 'orange',
            'honeydew', 'yellow', 'gold', 'goldenrod', 'brown',
            'blue', 'purple', 'darkorchid4', 'thistle', 'skyblue1',
            'green', 'palegreen1', 'darkgreen', 'aquamarine', 'darkolivegreen',
            ]

    def __init__(self, app_image):
        self.image = app_image
        super(AppPalette, self).__init__((35, 35), 4, 5, margin=2)
        self.selection = 0
        self.image.rect_color = pygame.color.Color(self.colors[self.selection])

    def num_items(self):
        return len(self.colors)

    def draw_item(self, surface, item_no, rect):
        d = -2 * self.sel_width
        r = rect.inflate(d, d)
        surface.fill(pygame.color.Color(self.colors[item_no]), r)

    def click_item(self, item_no, event):
        self.selection = item_no
        self.image.rect_color = pygame.color.Color(self.colors[item_no])

    def item_is_selected(self, item_no):
        return self.selection == item_no


class AppImage(Widget):

    rect_thick = 3
    draw_thick = 1

    def __init__(self, state):
        self.state = state
        super(AppImage, self).__init__(pygame.rect.Rect(0, 0,
                                                        constants.screen[0],
                                                        constants.screen[1]))
        self.mode = 'draw'
        self.rects = []
        self.images = []
        self.start_pos = None
        self.end_pos = None
        self.rect_color = pygame.color.Color('white')
        self.current_image = None
        self.place_image_menu = None
        self.close_button = BoomLabel('Close', font=get_font(20, 'Vera.ttf'))
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
        if self.state.current_detail:
            w, h = self.state.current_detail.get_detail_size()
            rect = pygame.rect.Rect(0, 0, w, h)
            self.close_button.rect.midbottom = rect.midbottom
            self.offset = (0, 0)
        else:
            self.offset = (-self.state.current_scene.OFFSET[0],
                           -self.state.current_scene.OFFSET[1])
        self.find_existing_intersects()

    def _get_scene(self):
        if self.state.current_detail:
            return self.state.current_detail
        else:
            return self.state.current_scene

    def find_existing_intersects(self):
        """Parse the things in the scene for overlaps"""
        scene = self._get_scene()
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
        scene = self._get_scene()
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

    def toggle_things(self):
        self.draw_things = not self.draw_things

    def toggle_thing_rects(self):
        self.draw_thing_rects = not self.draw_thing_rects
        scene = self._get_scene()
        for thing in scene.things.itervalues():
            if not self.draw_thing_rects:
                if not hasattr(thing, 'old_colour'):
                    thing.old_colour = thing._interact_hilight_color
                thing._interact_hilight_color = None
            else:
                thing._interact_hilight_color = thing.old_colour

    def toggle_images(self):
        self.draw_images = not self.draw_images

    def toggle_trans_images(self):
        self.trans_images = not self.trans_images
        self.invalidate()

    def toggle_rects(self):
        self.draw_rects = not self.draw_rects

    def toggle_toolbar(self):
        self.draw_toolbar = not self.draw_toolbar

    def toggle_zoom(self):
        self.zoom_display = not self.zoom_display

    def toggle_anim(self):
        self.draw_anim = not self.draw_anim

    def draw_mode(self):
        self.mode = 'draw'

    def del_mode(self):
        self.mode = 'del'
        self.start_pos = None
        self.end_pos = None

    def draw_sub_image(self, image, surface, cropped_rect):
        """Tweaked image drawing to avoid albow's centring the image in the
           subsurface"""
        surf = pygame.surface.Surface((cropped_rect.w, cropped_rect.h),
                                      SRCALPHA).convert_alpha()
        frame = surf.get_rect()
        imsurf = image.get_image().convert_alpha()
        r = imsurf.get_rect()
        r.topleft = frame.topleft
        if self.trans_images:
            surf.fill(pygame.color.Color(255, 255, 255, 96))
            surf.blit(imsurf, r, None, BLEND_RGBA_MIN)
        else:
            surf.blit(imsurf, r, None)
        surface.blit(surf, cropped_rect)

    def draw(self, surface):
        if self.zoom_display:
            base_surface = surface.copy()
            self.do_unzoomed_draw(base_surface)
            zoomed = pygame.transform.scale(base_surface,
                            (constants.zoom * constants.screen[0],
                             constants.zoom * constants.screen[1]))
            area = pygame.rect.Rect(self.zoom_offset[0], self.zoom_offset[1],
                                    self.zoom_offset[0] + constants.screen[0],
                                    self.zoom_offset[1] + constants.screen[1])
            surface.blit(zoomed, (0, 0), area)
        else:
            self.do_unzoomed_draw(surface)

    def do_unzoomed_draw(self, surface):
        if self.state.current_detail:
            if self.draw_things:
                self.state.current_detail.draw(surface, None)
            else:
                self.state.current_detail.draw_background(surface)
            # We duplicate Albow's draw logic here, so we zoom the close
            # button correctly
            r = self.close_button.get_rect()
            surf_rect = surface.get_rect()
            sub_rect = surf_rect.clip(r)
            try:
                sub = surface.subsurface(sub_rect)
                self.close_button.draw_all(sub)
            except ValueError, e:
                print 'Error, failed to draw close button', e
        else:
            if self.draw_things:
                self.state.current_scene.draw(surface, None)
            else:
                self.state.current_scene.draw_background(surface)
        if self.mode == 'draw' and self.start_pos and self.draw_rects:
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            rect.normalize()
            frame_rect(surface, self.rect_color, rect, self.draw_thick)
        if self.draw_rects:
            for (col, rect) in self.rects:
                frame_rect(surface, col, rect, self.rect_thick)
        if self.draw_images:
            for image in self.images:
                if image.rect.colliderect(surface.get_rect()):
                    cropped_rect = image.rect.clip(surface.get_rect())
                    self.draw_sub_image(image, surface, cropped_rect)
                else:
                    print 'image outside surface', image
            if self.current_image and self.mode == 'image':
                if self.current_image.rect.colliderect(surface.get_rect()):
                    cropped_rect = self.current_image.rect.clip(
                            surface.get_rect())
                    self.draw_sub_image(self.current_image, surface,
                                        cropped_rect)
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

    def print_objs(self):
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

    def image_load(self):
        image_path = ('%s/Resources/images/%s'
                      % (script_path, self.state.current_scene.FOLDER))
        imagename = request_old_filename(directory=image_path)
        try:
            image_data = pygame.image.load(imagename)
            self.current_image = Image(image_data)
            self.place_image_menu.enabled = True
            # ensure we're off screen to start
            self.current_image.rect = image_data.get_rect() \
                    .move(constants.screen[0] + constants.menu_width,
                          constants.screen[1])
        except pygame.error, e:
            print 'Unable to load image %s' % e

    def image_mode(self):
        self.mode = 'image'
        self.start_pos = None
        self.end_pos = None
        # So we do the right thing for off screen images
        self.old_mouse_pos = None

    def cycle_mode(self):
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

    def do_mouse_move(self, e):
        pos = self._conv_pos(e.pos)
        if not self.zoom_display:
            # Construct zoom offset from mouse pos
            self._make_zoom_offset(e.pos)
        if self.mode == 'image' and self.current_image:
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

    def key_down(self, e):
        if self.mode == 'image' and self.current_image:
            # Move the image by 1 pixel
            cur_pos = self.current_image.rect.center
            if e.key == K_LEFT:
                self.current_image.rect.center = (cur_pos[0] - 1, cur_pos[1])
            elif e.key == K_RIGHT:
                self.current_image.rect.center = (cur_pos[0] + 1, cur_pos[1])
            elif e.key == K_UP:
                self.current_image.rect.center = (cur_pos[0], cur_pos[1] - 1)
            elif e.key == K_DOWN:
                self.current_image.rect.center = (cur_pos[0], cur_pos[1] + 1)
        elif self.zoom_display:
            if e.key == K_LEFT:
                self._move_zoom(-1, 0)
            elif e.key == K_RIGHT:
                self._move_zoom(1, 0)
            elif e.key == K_UP:
                self._move_zoom(0, -1)
            elif e.key == K_DOWN:
                self._move_zoom(0, 1)

        if e.key == K_o:
            self.toggle_trans_images()
        elif e.key == K_t:
            self.toggle_things()
        elif e.key == K_r:
            self.toggle_thing_rects()
        elif e.key == K_i:
            self.toggle_images()
        elif e.key == K_d:
            self.toggle_rects()
        elif e.key == K_b:
            self.toggle_toolbar()
        elif e.key == K_z:
            self.toggle_zoom()
        elif e.key == K_a:
            self.toggle_anim()

    def mouse_down(self, e):
        pos = self._conv_pos(e.pos)
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
            scene = self._get_scene()
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
                    if image.rect.collidepoint(e.pos):
                        cand = image
                        break
                if cand:
                    self.images.remove(cand)
                    self.current_image = cand
                    # We want to move relative to the current mouse pos, so
                    self.old_mouse_pos = pos
                    self.invalidate()

    def mouse_up(self, e):
        if self.mode == 'draw':
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            rect.normalize()
            self.rects.append((self.rect_color, rect))
            self.start_pos = self.end_pos = None

    def mouse_drag(self, e):
        if self.mode == 'draw':
            self.end_pos = self._conv_pos(e.pos)
            self.invalidate()

    def animate(self):
        if self.draw_anim:
            if self.state.animate():
                self.invalidate()


class ModeLabel(BoomLabel):

    def __init__(self, app_image):
        self.app_image = app_image
        super(ModeLabel, self).__init__('Mode : ', 200,
                font=get_font(15, 'VeraBd.ttf'),
                fg_color=pygame.color.Color(128, 0, 255))
        self.rect.move_ip(805, 0)

    def draw_all(self, surface):
        self.set_text('Mode : %s' % self.app_image.mode)
        super(ModeLabel, self).draw_all(surface)


def make_button(text, action, ypos):
    button = Button(text, action=action, font=get_font(15, 'VeraBd.ttf'))
    button.align = 'l'
    button.rect = pygame.rect.Rect(0, 0, constants.menu_width,
                                   constants.menu_button_height)
    button.rect.move_ip(805, ypos)
    return button


class RectApp(Container):
    """The actual rect drawer main app"""
    def __init__(self, rect, gd):
        super(RectApp, self).__init__(rect, gd)


class RectEngine(object):
    """Engine for the rect drawer."""

    def __init__(self, gd, get_initial_state, scene, detail):
        self.state = None
        self._gd = gd
        rect = pygame.display.get_surface().get_rect()
        self.app = RectApp(rect, self._gd)

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
            surface = pygame.display.get_surface()
            self.app.draw(surface)
            pygame.display.flip()
            clock.tick(self._gd.constants.frame_rate)


class RectAppOld(RootWidget):
    """Handle the app stuff for the rect drawer"""

    def __init__(self, display, get_initial_state, scene, detail):
        super(RectApp, self).__init__(display)
        pygame.key.set_repeat(200, 100)
        state = get_initial_state()
        state.set_current_scene(scene)
        state.set_current_detail(detail)
        state.do_check = None

        self.image = AppImage(state)
        self.add(self.image)
        mode_label = ModeLabel(self.image)
        self.add(mode_label)
        y = mode_label.get_rect().h
        draw = make_button('Draw Rect', self.image.draw_mode, y)
        self.add(draw)
        y += draw.get_rect().h
        load_image = make_button("Load image", self.image.image_load, y)
        self.add(load_image)
        y += load_image.get_rect().h
        add_image = make_button("Place/Move images", self.image.image_mode, y)
        add_image.enabled = False
        self.add(add_image)
        self.image.place_image_menu = add_image
        y += add_image.get_rect().h
        cycle = make_button("Cycle interacts", self.image.cycle_mode, y)
        self.add(cycle)
        y += cycle.get_rect().h
        delete = make_button('Delete Objects', self.image.del_mode, y)
        self.add(delete)
        y += delete.get_rect().h
        palette = AppPalette(self.image)
        palette.rect.move_ip(810, y)
        self.add(palette)
        y += palette.get_rect().h
        print_rects = make_button("Print objects", self.image.print_objs, y)
        self.add(print_rects)
        y += print_rects.get_rect().h
        toggle_things = make_button("Show Things (t)",
                                    self.image.toggle_things, y)
        self.add(toggle_things)
        y += toggle_things.get_rect().h
        toggle_thing_rects = make_button("Show Thing Rects (r)",
                                         self.image.toggle_thing_rects, y)
        self.add(toggle_thing_rects)
        y += toggle_thing_rects.get_rect().h
        toggle_images = make_button("Show Images (i)",
                                    self.image.toggle_images, y)
        self.add(toggle_images)
        y += toggle_images.get_rect().h
        trans_images = make_button("Opaque Images (o)",
                                   self.image.toggle_trans_images, y)
        self.add(trans_images)
        y += trans_images.get_rect().h
        toggle_rects = make_button("Show Drawn Rects (d)",
                                   self.image.toggle_rects, y)
        self.add(toggle_rects)
        y += toggle_rects.get_rect().h
        toggle_toolbar = make_button("Show Toolbar (b)",
                                     self.image.toggle_toolbar, y)
        self.add(toggle_toolbar)
        y += toggle_toolbar.get_rect().h
        toggle_anim = make_button("Show Animations (a)",
                                  self.image.toggle_anim, y)
        self.add(toggle_anim)
        y += toggle_anim.get_rect().h
        toggle_zoom = make_button("Zoom (z)", self.image.toggle_zoom, y)
        self.add(toggle_zoom)
        y += toggle_zoom.get_rect().h
        quit_but = make_button("Quit", self.quit, 570)
        self.add(quit_but)
        self.set_timer(constants.frame_rate)

    def key_down(self, event):
        # Dispatch to image widget
        self.image.key_down(event)

    def mouse_delta(self, event):
        # We propogate mouse move from here to draw region, so images move
        # off-screen
        self.image.do_mouse_move(event)

    def begin_frame(self):
        self.image.animate()


def make_rect_display():
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((constants.screen[0]
        + constants.menu_width, constants.screen[1]))
