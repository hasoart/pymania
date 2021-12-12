import os
import json

import pygame
import audioplayer

from Core.Game import Game
from Utils.ui_objects import (
    TextBox,
    Button,
    Slider,
    DropDownList
)
from Utils.beatmap_utils import (
    get_beatmaps
)


class System:
    # class that have all parametries of during menu-pack
    def __init__(self, volume=0.5):
        """
        init for class System
        bg_image - image of background screen
        volume - volume of sound
        dim - characteristic of sound
        blur - characteristic of sound
        offset - contacting sound and picture
        """
        with open('./Settings/game_config.json', 'r') as f:
            sets = json.load(f)
        self.screen = pygame.display.set_mode((sets['width'], sets['height']))
        self.FPS = sets['FPS']
        self.Beatmaps_directory = sets['Beatmaps_directory']
        self.assets_directory = sets['assets_directory']
        self.sets = {'volume': volume}
        self.bg_image = 'bg_1.png'
        self.objects = []

        # open file with game constants:
        with open('./Settings/constants.json', 'r') as f:
            self.constants = json.load(f)

        # make background surface:
        self.bg_surface = pygame.image.load(os.path.join(self.assets_directory, self.bg_image)).convert_alpha()
        self.screen.blit(self.bg_surface, (0, 0))
        self.bg_surface = pygame.transform.smoothscale(self.bg_surface,
                                                       (self.screen.get_width(), self.screen.get_height()))
        self.bg_sound = os.path.join(self.assets_directory, 'song.mp3')
        self.start_music_player = audioplayer.AudioPlayer(self.bg_sound)
        self.in_menu = True
        self.audio_player = audioplayer.AudioPlayer(self.bg_sound)

        self.is_in_game = False

        self.place = None
        self.finished = False

        self.funtions_to_call = []

    def set(self, name, value):
        # set some parametres of game
        self.sets[name] = value

    def set_bg(self, bg):
        """
        set background
        :param bg: surface with image of new bg
        :return: None
        """
        self.bg_surface = bg
        self.bg_surface = pygame.transform.smoothscale(self.bg_surface,
                                                       (self.screen.get_width(), self.screen.get_height()))

    def menu(self):
        # open menu
        # read constants from file:
        self.place = self.menu
        self.in_menu = True
        screen = self.screen
        w = screen.get_width()
        h = screen.get_height()
        folder = self.assets_directory
        const = self.constants['menu']
        box_size = self.constants['box_size']
        font = self.constants['font']
        # make buttons and textboxes:
        menu = TextBox((w * const['menu'][0], h * const['menu'][1]),
                       font,
                       self.constants['colors']['textbox'], 'Menu', 'center',
                       os.path.join(folder, 'box.jpg'), box_size)
        setting = Button(
            (w * const['settings'][0], h * const['settings'][1]), font,
            self.constants['colors']['button'], 'Settings', 'center', os.path.join(folder, 'rect.png'),
            self.settings, box_size)
        start = Button((w * const['start'][0], h * const['start'][1]), font,
                       self.constants['colors']['button'], 'Start', 'center', os.path.join(folder, 'rect.png'),
                       self.start, box_size)
        _exit = Button((w * const['exit'][0], h * const['exit'][1]), font,
                       self.constants['colors']['button'], 'Exit', 'center', os.path.join(folder, 'rect.png'),
                       self.exit_screensaver,
                       box_size)
        self.objects = [menu, setting, start, _exit]

        self.funtions_to_call = []

    def settings(self):
        # open settings-menu
        # read contants from file
        screen = self.screen
        w = screen.get_width()
        h = screen.get_height()
        folder = self.assets_directory
        const = self.constants['settings']
        box_size = self.constants['box_size']
        circle_size = self.constants['circle_size']
        color_on = self.constants['colors']['slider_on']
        color_off = self.constants['colors']['slider_off']
        font = self.constants['font']
        # make buttons and textboxes, sliders:
        menu_box = TextBox((w * const['menu_box'][0], h * const['menu_box'][1]), font,
                           self.constants['colors']['textbox'], 'Settings menu', 'center',
                           os.path.join(folder, 'box.jpg'), box_size)
        volume = TextBox((w * const['volume'][0], h * const['volume'][1]), font,
                         self.constants['colors']['textbox'], 'Volume', 'left', os.path.join(folder, 'box.jpg'),
                         box_size)
        volume_slider = Slider((w * const['volume_slider'][0], h * const['volume_slider'][1]),
                               os.path.join(folder, 'circle.png'), color_on, color_off,
                               (w * const['volume_slider_size'][0], h * const['volume_slider_size'][1]), self, 'volume',
                               font, self.constants['colors']['textbox'], self.sets['volume'], circle_size)
        bg = TextBox((w * const['bg'][0], h * const['bg'][1]), font,
                     self.constants['colors']['textbox'], 'Choose background:', 'left', os.path.join(folder, 'box.jpg'),
                     box_size)
        bg_1 = Button((w * const['bg_1'][0], h * const['bg_1'][1]), font,
                      self.constants['colors']['common'], None, 'left', os.path.join(folder, 'bg_1.png'),
                      [self.set_bg], box_size=box_size,
                      size=(int(w * const['bg_button_size'][0]), int(h * const['bg_button_size'][1])))
        bg_2 = Button((w * const['bg_2'][0], h * const['bg_2'][1]), font,
                      self.constants['colors']['common'], None, 'left', os.path.join(folder, 'bg_2.png'),
                      [self.set_bg], box_size=box_size,
                      size=(int(w * const['bg_button_size'][0]), int(h * const['bg_button_size'][1])))
        bg_3 = Button((w * const['bg_3'][0], h * const['bg_3'][1]), font,
                      self.constants['colors']['common'], None, 'left', os.path.join(folder, 'bg_3.png'),
                      [self.set_bg], box_size=box_size,
                      size=(int(w * const['bg_button_size'][0]), int(h * const['bg_button_size'][1])))
        _exit = Button((w * const['exit'][0], h * const['exit'][1]), font,
                       self.constants['colors']['button'], 'Back', 'left', os.path.join(folder, 'rect.png'), self.place,
                       box_size)
        self.objects = [menu_box, volume, volume_slider, _exit, bg_1, bg, bg_2, bg_3]
        self.place = self.settings

        self.funtions_to_call = []

    def start(self):
        self.in_menu = False
        screen = self.screen
        self.place = self.start
        w = screen.get_width()
        h = screen.get_height()
        folder = self.assets_directory
        const = self.constants['start']
        # take information about tracks into files:
        beatmaps = get_beatmaps(self.Beatmaps_directory)
        objects = []

        # add songs into drop_down format:
        for beat_map in beatmaps:
            song = []
            file = {'text': beat_map['title'], 'music': beat_map['music_path'], 'type': 'main',
                    'bg_image': beat_map['bg_image'], 'preview': beat_map['preview'], 'title': beat_map['title'],
                    'artist': beat_map['artist'], 'rect_image': os.path.join(self.assets_directory, 'rect_image.jpg')}
            song.append(file)
            for dif in beat_map['diffs']:
                file = {'music': beat_map['music_path'], 'type': 'not_main', 'bg_image': beat_map['bg_image'],
                        'preview': beat_map['preview'], 'text': str(list(dif.keys())[0]),
                        'rect_image': os.path.join(self.assets_directory, 'rect_image.jpg')}
                diff = dif[str(list(dif.keys())[0])]
                file['func'] = [self.start_game, self.screen, beat_map['beatmap_directory'], diff, self.sets['volume'] * 100]
                song.append(file)

            objects.append(song)

        _map = DropDownList((w * const['drop_down_list'][0], h * const['drop_down_list'][1]),
                            os.path.join(self.assets_directory, 'arrow.png'), self.constants['font'],
                            'black', objects, self.constants, self, self.audio_player)
        # add button:
        setting = Button(
            (w * const['settings'][0], h * const['settings'][1]), self.constants['font'],
            self.constants['colors']['button'], '', 'center', os.path.join(folder, 'settings.png'),
            self.settings,
            box_size=self.constants['box_size'],
            size=(int(w * const['settings_size'][0]), int(h * const['settings_size'][1])))
        self.objects = [_map, setting]

        self.funtions_to_call = [_map.mute]

    def play(self, first_time=True):
        # start menu-window
        FPS = self.FPS

        pygame.display.update()
        clock = pygame.time.Clock()
        if first_time:
            self.menu()
            self.start_music_player.volume = int(100 * self.sets['volume'])
            self.start_music_player.play(loop=True)
        else:
            self.start()

        while not self.finished:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
                for obj in self.objects:
                    if type(obj) != TextBox:
                        obj.click(event)

            if self.in_menu:
                self.start_music_player.resume()
            else:
                self.start_music_player.pause()

            # draw objects:
            self.screen.blit(self.bg_surface, (0, 0))
            for obj in self.objects:
                self.screen.blit(obj.get_surface(), obj.position)

            pygame.display.update()
        pygame.quit()

    def exit_screensaver(self):
        print('exit')
        self.finished = True
        exit()

    def start_game(self, screen, beat_map, diff, volume):
        print(beat_map, "|||||", diff)
        self.audio_player.close()
        self.start_music_player.close()
        self.in_menu = False
        self.is_in_game = True
        for function in self.funtions_to_call:
            function()
        game = Game(screen, beat_map, diff, self, volume=volume)
        game.start()
