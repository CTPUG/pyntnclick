# Quickly hacked together helper for working out
# interactive regions in Suspended Sentence

import sys
import os.path

script_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(script_path)

from albow.root import RootWidget
from albow.utils import frame_rect
from albow.widget import Widget
from albow.controls import Button, Image
from albow.palette_view import PaletteView
from albow.file_dialogs import request_old_filename
from albow.resource import get_font
from pygame.locals import SWSURFACE
import pygame
from pygame.colordict import THECOLORS

from gamelib import constants
constants.DEBUG = True

from gamelib import state
state.DEBUG_RECTS = True
from gamelib.widgets import BoomLabel




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
        super(AppPalette, self).__init__((35, 35), 5, 5, margin=2)
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
        super(AppImage, self).__init__(pygame.rect.Rect(0, 0, 800, 600))
        self.mode = 'draw'
        self.rects = []
        self.images = []
        self.start_pos = None
        self.end_pos = None
        self.draw_color = pygame.color.Color('white')
        self.rect_color = pygame.color.Color('white')
        self.current_image = None
        self.place_image_menu = None
        self.close_button = BoomLabel('Close', font=get_font(20, 'Vera.ttf'))
        self.close_button.fg_color = (0, 0, 0)
        self.close_button.bg_color = (0, 0, 0)
        if self.state.current_detail:
            w, h = self.state.current_detail.get_detail_size()
            rect = pygame.rect.Rect(0, 0, w, h)
            self.close_button.rect.midbottom = rect.midbottom
            self.add(self.close_button)
            self.offset = (0, 0)
        else:
            self.offset = (-self.state.current_scene.OFFSET[0], - self.state.current_scene.OFFSET[1])
        self.draw_rects = True
        self.draw_things = True
        self.draw_thing_rects = True
        self.draw_images = True
        self.draw_toolbar = True

    def toggle_things(self):
        self.draw_things = not self.draw_things

    def toggle_thing_rects(self):
        self.draw_thing_rects = not self.draw_thing_rects
        if self.state.current_detail:
            scene = self.state.current_detail
        else:
            scene = self.state.current_scene
        for thing in scene.things.itervalues():
            if not self.draw_thing_rects:
                if not hasattr(thing, 'old_colour'):
                    thing.old_colour = thing._interact_hilight_color
                thing._interact_hilight_color = None
            else:
                thing._interact_hilight_color = thing.old_colour

    def toggle_images(self):
        self.draw_images = not self.draw_images

    def toggle_rects(self):
        self.draw_rects = not self.draw_rects

    def toggle_toolbar(self):
        self.draw_toolbar = not self.draw_toolbar

    def draw_mode(self):
        self.mode = 'draw'

    def del_mode(self):
        self.mode = 'del'
        self.start_pos = None
        self.end_pos = None

    def draw(self, surface):
        if self.state.current_detail:
            if self.draw_things:
                self.state.draw_detail(surface, None)
            else:
                self.state.current_detail.draw_background(surface)
        else:
            if self.draw_things:
                self.state.draw(surface, None)
            else:
                self.state.current_scene.draw_background(surface)
        if self.mode == 'draw' and self.start_pos and self.draw_rects:
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            frame_rect(surface, self.draw_color, rect, self.draw_thick)
        if self.draw_rects:
            for (col, rect) in self.rects:
                frame_rect(surface, col, rect, self.rect_thick)
        if self.draw_images:
            for image in self.images:
                if image.rect.colliderect(surface.get_rect()):
                    cropped_rect = image.rect.clip(surface.get_rect())
                    sub = surface.subsurface(cropped_rect)
                    image.draw(sub)
                else:
                    print 'image outside surface', image
            if self.current_image and self.mode == 'image':
                if self.current_image.rect.colliderect(surface.get_rect()):
                    cropped_rect = self.current_image.rect.clip(surface.get_rect())
                    sub = surface.subsurface(cropped_rect)
                    self.current_image.draw(sub)
        if self.draw_toolbar:
            toolbar_rect = pygame.rect.Rect(0, 550, 800, 50)
            tb_surf = surface.subsurface(0, 550, 800, 50).convert_alpha()
            tb_surf.fill(pygame.color.Color(127, 0, 0, 191))
            surface.blit(tb_surf, (0, 550))
            # frame_rect(surface, (127, 0, 0), toolbar_rect, 2)

    def _make_dict(self):
        d = {}
        for col, rect in self.rects:
            col = (col.r, col.g, col.b)
            d.setdefault(col, [])
            d[col].append(rect)
        return d

    def print_objs(self):
        d = self._make_dict()
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

    def image_load(self):
        image_path= '%s/Resources/images/%s' % (script_path, self.state.current_scene.FOLDER)
        imagename = request_old_filename(directory=image_path)
        try:
            image_data = pygame.image.load(imagename)
            self.current_image = Image(image_data)
            self.place_image_menu.enabled = True
            # ensure we're off screen to start
            self.current_image.rect = image_data.get_rect().move(1000, 600)
        except pygame.error, e:
            print 'Unable to load image %s' % e

    def image_mode(self):
        self.mode = 'image'
        self.start_pos = None
        self.end_pos = None

    def mouse_move(self, e):
        if self.mode == 'image' and self.current_image:
            self.current_image.rect.topleft = e.pos
            self.invalidate()

    def mouse_down(self, e):
        if self.mode == 'del':
            pos = e.pos
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
        elif self.mode == 'draw':
            self.start_pos = e.pos
            self.end_pos = e.pos
        elif self.mode == 'image':
            if self.current_image:
                self.images.append(self.current_image)
                self.current_image = None
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
            self.end_pos = e.pos
            self.invalidate()

def make_button(text, action, ypos):
    button = Button(text, action=action)
    button.align = 'l'
    button.rect = pygame.rect.Rect(0, 0, 200, 35)
    button.rect.move_ip(805, ypos)
    return button

if __name__ == "__main__":
    # FIXME: should load an actual scene with current things, not just a
    # background image
    if len(sys.argv) < 2:
        print 'Please provide a scene name'
        sys.exit(0)
    pygame.display.init()
    pygame.font.init()
    display = pygame.display.set_mode((1000, 600))
    state = state.initial_state()
    if len(sys.argv) < 3:
        try:
            state.set_current_scene(sys.argv[1])
            state.do_check = None
        except KeyError:
            print 'Invalid scene name'
            sys.exit(1)
    else:
        try:
            state.set_current_scene(sys.argv[1])
            state.set_current_detail(sys.argv[2])
            state.do_check = None
        except KeyError:
            print 'Invalid scene name'
            sys.exit(1)
    app = RootWidget(display)
    image = AppImage(state)
    app.add(image)
    draw = make_button('Draw Rect', image.draw_mode, 0)
    app.add(draw)
    load_image = make_button("Load image", image.image_load, 35)
    app.add(load_image)
    add_image = make_button("Place/Move images", image.image_mode, 70)
    add_image.enabled = False
    app.add(add_image)
    image.place_image_menu = add_image
    delete = make_button('Delete Objects', image.del_mode, 105)
    app.add(delete)
    palette = AppPalette(image)
    palette.rect.move_ip(810, 140)
    app.add(palette)
    print_rects = make_button("Print objects", image.print_objs, 300)
    app.add(print_rects)
    toggle_things = make_button("Toggle Things", image.toggle_things, 335)
    app.add(toggle_things)
    toggle_thing_rects = make_button("Toggle Thing Rects", image.toggle_thing_rects, 370)
    app.add(toggle_thing_rects)
    toggle_images = make_button("Toggle Images", image.toggle_images, 405)
    app.add(toggle_images)
    toggle_rects = make_button("Toggle Rects", image.toggle_rects, 440)
    app.add(toggle_rects)
    toggle_toolbar = make_button("Toggle Toolbar", image.toggle_toolbar, 475)
    app.add(toggle_toolbar)
    quit_but = make_button("Quit", app.quit, 565)
    app.add(quit_but)
    app.run()
