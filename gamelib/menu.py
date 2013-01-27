# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from pyntnclick.menuscreen import MenuScreen


class SSMenuScreen(MenuScreen):
    BACKGROUND_IMAGE = 'splash/splash.png'

    def make_new_game_button(self):
        return self.make_image_button((16, 523), 'splash/play.png')

    def make_resume_game_button(self):
        return self.make_image_button((256, 523), 'splash/resume.png')

    def make_quit_button(self):
        return self.make_image_button((580, 523), 'splash/quit.png')
