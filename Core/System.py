import os
import json
from typing import Callable

import pygame
import audioplayer

from Core.Game import Game
from Utils.ui_objects import (
    TextBox,
    Button,
    Slider,
    DropDownList,
    smartscale
)
from Utils.beatmap_utils import (
    get_beatmaps
)


class System:
    # class that have all parametries of during menu-pack
    def __init__(self) -> None:
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
        self.width, self.height = sets['width'], sets['height']

        self.FPS = sets['FPS']
        self.Beatmaps_directory = sets['Beatmaps_directory']
        self.assets_directory = sets['assets_directory']
        self.sets = {'volume': sets['volume']}
        self.objects = []

        # open file with game constants:
        with open('./Settings/constants.json', 'r') as f:
            self.constants = json.load(f)

        self.bg_image = self.constants['settings']['backgrounds'][0]['image']

        # make background surface:
        self.bg_surface = pygame.image.load(os.path.join(self.assets_directory, self.bg_image)).convert_alpha()
        self.screen.blit(self.bg_surface, (0, 0))
        self.bg_surface = smartscale(self.bg_surface, (self.screen.get_width(), self.screen.get_height()))
        self.bg_sound = os.path.join(self.assets_directory, 'song.mp3')
        self.start_music_player = audioplayer.AudioPlayer(self.bg_sound)
        self.in_menu = True
        self.audio_player = audioplayer.AudioPlayer(self.bg_sound)

        self.is_in_game = False
        self.finished = False
        self.first_time = True

        self.place = None
        self.last_place = None

        self.menu_objects = self.get_menu()
        self.settings_objects = self.get_settings()
        self.start_objects = self.get_start()

        self.funtions_to_call = []

    def set(self, name, value) -> None:
        # set some parametres of game
        self.sets[name] = value

    def set_bg(self, bg_image: str) -> None:
        """
        set background
        :param bg_image: background filename
        :return: None
        """
        bg = pygame.image.load(os.path.join(self.assets_directory, bg_image))
        self.bg_surface = smartscale(bg, (self.screen.get_width(), self.screen.get_height()))

    def get_menu(self) -> list:
        # open menu
        folder = self.assets_directory
        const = self.constants['menu']
        box_size = self.constants['box_size']
        font = self.constants['font']
        # make buttons and textboxes:
        menu = TextBox((self.width * const['menu'][0], self.height * const['menu'][1]),
                       font,
                       self.constants['colors']['textbox'], 'Menu', 'center',
                       os.path.join(folder, 'box.jpg'), box_size)
        setting = Button(
            (self.width * const['settings'][0], self.height * const['settings'][1]), font,
            self.constants['colors']['button'], 'Settings', 'center', os.path.join(folder, 'rect.png'),
            [self.switch, (self.settings,)], box_size)
        start = Button((self.width * const['start'][0], self.height * const['start'][1]), font,
                       self.constants['colors']['button'], 'Start', 'center', os.path.join(folder, 'rect.png'),
                       [self.switch, (self.start,)], box_size)
        _exit = Button((self.width * const['exit'][0], self.height * const['exit'][1]), font,
                       self.constants['colors']['button'], 'Exit', 'center', os.path.join(folder, 'rect.png'),
                       [self.exit_screensaver, ()],
                       box_size)

        return [menu, setting, start, _exit]

    def get_settings(self) -> list:
        # open settings-menu
        # read contants from file
        folder = self.assets_directory
        const = self.constants['settings']
        box_size = self.constants['box_size']
        circle_size = self.constants['circle_size']
        color_on = self.constants['colors']['slider_on']
        color_off = self.constants['colors']['slider_off']
        font = self.constants['font']

        # make buttons and textboxes, sliders:
        menu_box = TextBox((self.width * const['menu_box'][0], self.height * const['menu_box'][1]), font,
                           self.constants['colors']['textbox'], 'Settings menu', 'center',
                           os.path.join(folder, 'box.jpg'), box_size)

        volume = TextBox((self.width * const['volume'][0], self.height * const['volume'][1]), font,
                         self.constants['colors']['textbox'], 'Volume', 'left', os.path.join(folder, 'box.jpg'),
                         box_size)

        volume_slider = Slider((self.width * const['volume_slider'][0], self.height * const['volume_slider'][1]),
                               os.path.join(folder, 'circle.png'), color_on, color_off,
                               (self.width * const['volume_slider_size'][0],
                                self.height * const['volume_slider_size'][1]), self, 'volume',
                               font, self.constants['colors']['textbox'], self.sets['volume'], circle_size)

        bg = TextBox((self.width * const['bg'][0], self.height * const['bg'][1]), font,
                     self.constants['colors']['textbox'], 'Choose background:', 'left', os.path.join(folder, 'box.jpg'),
                     box_size)

        bg_buttons = []
        for background in const['backgrounds']:
            bg_image = background['image']
            pos = background['pos']
            button = Button((self.width * pos[0], self.height * pos[1]), font,
                            self.constants['colors']['common'], None, 'left', os.path.join(folder, bg_image),
                            [self.set_bg, (bg_image,)], box_size=box_size,
                            size=(int(self.width * const['bg_button_size'][0]), int(self.height * const['bg_button_size'][1])))
            bg_buttons.append(button)

        _exit = Button((self.width * const['exit'][0], self.height * const['exit'][1]), font,
                       self.constants['colors']['button'], 'Back', 'left', os.path.join(folder, 'rect.png'),
                       [self.switch_back, ()], box_size)

        return [menu_box, volume, volume_slider, _exit, bg] + bg_buttons

    def get_start(self) -> list:
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
                file['func'] = [self.start_game, self.screen, beat_map['beatmap_directory'], diff]
                song.append(file)

            objects.append(song)

        _map = DropDownList((self.width * const['drop_down_list'][0], self.height * const['drop_down_list'][1]),
                            os.path.join(self.assets_directory, 'arrow.png'), self.constants['font'],
                            'black', objects, self.constants, self, self.audio_player,
                            (int(self.width * const['drop_down_list_size'][0]),
                             int(self.height * const['drop_down_list_size'][1])))
        # add button:
        setting = Button(
            (self.width * const['settings'][0], self.height * const['settings'][1]), self.constants['font'],
            self.constants['colors']['button'], '', 'center', os.path.join(folder, 'settings.png'),
            [self.switch, (self.settings,)],
            box_size=self.constants['box_size'],
            size=(int(self.width * const['settings_size']), int(self.width * const['settings_size'])))

        # WARNING: First argument must be _map, as it is used in method start!
        return [_map, setting]

    def menu(self) -> None:
        self.place = self.menu
        self.in_menu = True
        self.funtions_to_call = []
        self.objects = self.menu_objects

    def settings(self) -> None:
        self.place = self.settings
        self.funtions_to_call = []
        self.objects = self.settings_objects

    def start(self) -> None:
        self.in_menu = False
        self.place = self.start
        self.funtions_to_call = [self.start_objects[0].mute]
        self.objects = self.start_objects

    def switch(self, destination: Callable) -> None:
        self.last_place = self.place
        self.place = destination
        self.place()

    def switch_back(self) -> None:
        self.place, self.last_place = self.last_place, self.place
        self.place()
        self.start_music_player.volume = int(100 * self.sets['volume'])
        self.audio_player.volume = int(100 * self.sets['volume'])

    def play(self) -> None:
        # start menu-window
        FPS = self.FPS

        pygame.display.update()
        clock = pygame.time.Clock()
        if self.first_time:
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

    def exit_screensaver(self) -> None:
        with open('./Settings/game_config.json', 'r') as f:
            game_config = json.load(f)
        game_config['volume'] = self.sets['volume']
        with open('./Settings/game_config.json', 'w') as f:
            json.dump(game_config, f, indent=4)
        exit()

    def start_game(self, screen: pygame.Surface, beat_map: str, diff: str) -> None:
        print(beat_map, "----", diff)
        self.audio_player.close()
        self.start_music_player.close()
        self.in_menu = False
        self.is_in_game = True

        for function in self.funtions_to_call:
            function()

        game = Game(screen, beat_map, diff, self, volume=int(100* self.sets['volume']))
        exit_code = game.start()

        if exit_code == -1:
            self.exit_screensaver()
