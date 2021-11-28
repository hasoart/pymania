import os
import time
import json

import pygame as pg
import pygame.draw as draw

from beatmap_parser import *
from Track import Track


class GameMaster:
    def __init__(self, surface, beatmap_folder, beatmap):
        """
        :param surface: Поверхность игры
        :param beatmap_folder: путь директории карты
        :param beatmap: имя карты (путь относительно beatmap)
        """

        self.surface = surface
        self.beatmap_folder = beatmap_folder
        self.beatmap = beatmap_folder + '/' + beatmap

        self.metadata = get_metadata(beatmap)

        self.width, self.height = surface.get_size()

        with open('game_config.json', 'r') as f:
            game_config = json.load(f)

        with open('settings.json', 'r') as f:
            settings = json.load(f)

        self.tracks = []

        self.track_count = int(self.metadata['CircleSize'])

        for i in range(self.track_count):
            self.tracks += [Track(i, settings[f'{self.track_count}k_keys'][i], hit_distance=game_config['hit_distance'],
                                  width=game_config['track_width'], height=self.height,
                                  note_height=game_config['note_height'], hold_width=game_config['hold_width'],
                                  bg_color=game_config['track_color'], note_color=game_config['note_color'],
                                  hold_color=game_config['hold_color'])]

        self.score = 0

    def render(self):
        # TODO
        pass
