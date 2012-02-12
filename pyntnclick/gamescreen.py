# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from pygame import Rect, Surface
from pygame.color import Color
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_ESCAPE

from pyntnclick.cursor import CursorScreen
from pyntnclick.engine import Screen
from pyntnclick.state import handle_result
from pyntnclick.widgets.base import Widget, Container
from pyntnclick.widgets.text import TextButton
from pyntnclick.widgets.imagebutton import ImageButtonWidget

# XXX: Need a way to get at the constants.
from pyntnclick.constants import GameConstants
constants = GameConstants()
SCREEN = constants.screen
LEAVE = constants.leave


class InventoryView(Widget):
    # TODO: Make this work again

    sel_color = Color("yellow")
    sel_width = 2

    def __init__(self, rect, gd, screen):
        self.bsize = gd.constants.button_size
        super(InventoryView, self).__init__(rect, gd)
        self.screen = screen
        self.game = screen.game
        self.state_widget = screen.state_widget
        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.update_surface()

    def update_surface(self):
        self.surface = Surface(self.rect.size)
        for item_no in range(self.num_items()):
            self.draw_item(self.surface, item_no,
                           Rect((item_no * self.bsize, 0),
                                (self.bsize, self.bsize)))

    def draw(self, surface):
        self.update_surface()
        surface.blit(self.surface, self.rect)

    def num_items(self):
        return len(self.game.inventory)

    def draw_item(self, surface, item_no, rect):
        item_image = self.game.inventory[item_no].get_inventory_image()
        surface.blit(item_image, rect, None)

    def click_item(self, item_no, event):
        item = self.game.inventory[item_no]
        print "Using:", item
        if self.item_is_selected(item_no):
            self.unselect()
        elif item.is_interactive(self.game.tool):
            result = item.interact(self.game.tool)
            handle_result(result, self.state_widget)
        else:
            self.game.set_tool(self.game.inventory[item_no])

    def mouse_down(self, event, widget):
        if event.button != 1:
            return self.game.cancel_doodah(self.screen)
        x, y = self.global_to_local(event.pos)
        item_no = x / self.bsize
        if item_no < self.num_items():
            self.click_item(item_no, event)
        else:
            print "No item."

    def item_is_selected(self, item_no):
        return self.game.tool is self.game.inventory[item_no]

    def unselect(self):
        self.game.set_tool(None)


class StateWidget(Container):

    def __init__(self, rect, gd, screen):
        super(StateWidget, self).__init__(rect, gd)
        self.screen = screen
        self.game = screen.game
        self.detail = DetailWindow(rect, gd, screen)
        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.add_callback(MOUSEMOTION, self.mouse_move)

    def draw(self, surface):
        self.game.current_scene.draw(surface, self)
        # Pass to container to draw children
        super(StateWidget, self).draw(surface)
        #self.animate()
        # XXX: Work out if we still need this
        # if self.game.previous_scene and self.game.do_check == LEAVE:
        #    # We still need to handle leave events, so still display the scene
        #    self.game.previous_scene.draw(surface, self)
        #else:
        #    self.game.current_scene.draw(surface, self)
        # We draw descriptions here, so we do the right thing
        # with detail views
        if self.game.current_detail:
            self.game.current_detail.draw_description(surface)
        else:
            self.game.current_scene.draw_description(surface)

    def mouse_down(self, event, widget):
        if self.game.current_detail:
            return self.detail.mouse_down(event, widget)
        self.mouse_move(event, widget)
        if event.button != 1:  # We have a right/middle click
            self.game.cancel_doodah(self.screen)
        else:
            result = self.game.interact(event.pos)
            handle_result(result, self)

    def animate(self):
        # XXX: if self.game.animate():
            # queue a redraw
        #    self.invalidate()
        # We do this here so we can get enter and leave events regardless
        # of what happens
        result = self.game.check_enter_leave(self.screen)
        handle_result(result, self)
        if self.game.current_detail:
            self.game.current_detail.animate()
        else:
            self.game.current_scene.animate()

    def mouse_move(self, event, widget):
        if self.game.current_detail:
            return self.detail.mouse_move(event, widget)
        self.game.highlight_override = False
        self.game.current_scene.mouse_move(event.pos)
        self.game.old_pos = event.pos

    def show_message(self, message, style=None):
        # Display the message as a modal dialog
        print message
        # XXX: MessageDialog(self.screen, message, 60, style=style).present()
        # queue a redraw to show updated state
        # XXX: self.invalidate()
        # The cursor could have gone anywhere
        # XXX: if self.subwidgets:
        #    self.subwidgets[0]._mouse_move(mouse.get_pos())
        # else:
        #    self._mouse_move(mouse.get_pos())

    def show_detail(self, detail):
        self.clear_detail()
        detail_obj = self.game.set_current_detail(detail)
        self.add(self.detail)
        detail_rect = Rect((0, 0), detail_obj.get_detail_size())
        # Centre the widget
        detail_rect.center = self.rect.center
        self.detail.set_image_rect(detail_rect)
        self.game.do_enter_detail()

    def clear_detail(self):
        """Hide the detail view"""
        if self.game.current_detail is not None:
            self.remove(self.detail)
            self.game.do_leave_detail()
            self.game.set_current_detail(None)
            #self._mouse_move(mouse.get_pos())

    def end_game(self):
        self.screen.change_screen('end')


class DetailWindow(Container):
    def __init__(self, rect, gd, screen):
        super(DetailWindow, self).__init__(rect, gd)
        self.image_rect = None
        self.screen = screen
        self.game = screen.game
        self.border_width = 5
        self.border_color = (0, 0, 0)
        # parent only gets set when we get added to the scene
        self.close = TextButton(Rect(0, 0, 0, 0), self.gd,
                text='Close')
        self.close.add_callback('clicked', self.close_but)
        self.add(self.close)

    def close_but(self, ev, widget):
        self.parent.clear_detail()

    def end_game(self):
        self.parent.end_game()

    def set_image_rect(self, rect):
        bw = self.border_width
        self.image_rect = rect
        self.rect = rect.inflate(bw * 2, bw * 2)
        self.close.rect.midbottom = rect.midbottom

    def draw(self, surface):
        # scene_surface = self.get_root().surface.subsurface(self.parent.rect)
        # overlay = scene_surface.convert_alpha()
        # overlay.fill(Color(0, 0, 0, 191))
        # scene_surface.blit(overlay, (0, 0))
        self.game.current_detail.draw(
            surface.subsurface(self.image_rect), self)
        super(DetailWindow, self).draw(surface)

    def mouse_down(self, event, widget):
        self.mouse_move(event, widget)
        if event.button != 1:  # We have a right/middle click
            self.game.cancel_doodah(self.screen)
        else:
            result = self.game.interact_detail(
                self.global_to_local(event.pos))
            handle_result(result, self)

    def mouse_move(self, event, widget):
        self._mouse_move(event.pos)

    def _mouse_move(self, pos):
        self.game.highlight_override = False
        self.game.current_detail.mouse_move(self.global_to_local(pos))

    def show_message(self, message, style=None):
        # self.parent.show_message(message, style)
        # self.invalidate()
        print message


class ToolBar(Container):
    def __init__(self, rect, gd, screen):
        self.screen = screen
        button_size = gd.constants.button_size

        if not isinstance(rect, Rect):
            rect = Rect(rect, (gd.constants.scene_size[0], button_size))
        super(ToolBar, self).__init__(rect, gd)

        self.bg_color = (31, 31, 31)
        self.left = self.rect.left

        self.menu_button = self.add_tool(
            0, TextButton, gd, "Menu", fontname="VeraBd.ttf", color="red",
            padding=2, border=0)
        self.menu_button.add_callback(MOUSEBUTTONDOWN, self.menu_callback)

        hand_image = gd.resource.get_image('items', 'hand.png')
        self.hand_button = self.add_tool(
            None, ImageButtonWidget, gd, hand_image)
        self.hand_button.add_callback(MOUSEBUTTONDOWN, self.hand_callback)

        self.inventory = self.add_tool(
            self.rect.width - self.left, InventoryView, gd, screen)

    def add_tool(self, width, cls, *args, **kw):
        rect = (self.left, self.rect.top)
        if width is not None:
            rect = Rect(rect, (width, self.rect.height))
        tool = cls(rect, *args, **kw)
        self.add(tool)
        self.left += tool.rect.width
        return tool

    def draw(self, surface):
        bg = Surface(self.rect.size)
        bg.fill(self.bg_color)
        surface.blit(bg, self.rect)
        super(ToolBar, self).draw(surface)

    def hand_callback(self, event, widget):
        self.inventory.unselect()

    def menu_callback(self, event, widget):
        self.screen.change_screen('menu')


class GameScreen(CursorScreen):

    def setup(self):
        super(GameScreen, self).setup()
        self.running = False
        self.create_initial_state = self.gd.initial_state
        self.container.add_callback(KEYDOWN, self.key_pressed)
        self.state_widget = None

    def _clear_all(self):
        for widget in self.container.children[:]:
            self.container.remove(widget)

    def process_event(self, event_name, data):
        if event_name == 'restart':
            self.start_game()

    def start_game(self):
        self._clear_all()
        toolbar_height = self.gd.constants.button_size
        rect = Rect(0, 0, self.surface_size[0],
                    self.surface_size[1] - toolbar_height)
        self.game = self.create_initial_state()
        self.state_widget = StateWidget(rect, self.gd, self)
        self.container.add(self.state_widget)

        self.toolbar = ToolBar((0, rect.height), self.gd, self)
        self.inventory = self.toolbar.inventory
        self.container.add(self.toolbar)

        self.running = True

    def animate(self):
        """Animate the state widget"""
        if self.state_widget:
            self.state_widget.animate()

    def key_pressed(self, event, widget):
        if event.key == K_ESCAPE:
            self.change_screen('menu')


class DefEndScreen(Screen):
    """A placeholder 'Game Over' screen so people can get started easily"""

    def setup(self):
        self.background = self.resource.get_image('pyntnclick/end.png')

    def draw(self, surface):
        surface.blit(self.background, (0, 0))


class DefMenuScreen(Screen):
    """A placeholder Start screen so people can get started easily"""

    def setup(self):
        self.background = self.resource.get_image('pyntnclick/start.png')

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
