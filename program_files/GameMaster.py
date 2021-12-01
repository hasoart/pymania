import os
import time
import json

import pygame as pg
import pygame.draw as draw
import audioplayer

from beatmap_parser import *
from settings import settings
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
        self.beatmap = os.path.join(beatmap_folder, beatmap)

        self.metadata = get_metadata(self.beatmap)
        self.hitobjects = get_hitobjects(self.beatmap)

        self.width, self.height = surface.get_size()

        with open('game_config.json', 'r') as f:
            self.game_config = json.load(f)

        self.settings = settings

        self.tracks = []

        self.track_count = int(self.metadata['CircleSize'])
        self.fall_time = 1000

        for i in range(self.track_count):
            self.tracks += [Track(i, self.settings[f'{self.track_count}k_keys'][i], hit_distance=self.game_config['hit_distance'],
                                  width=self.game_config['track_width'], height=self.height,
                                  note_height=self.game_config['note_height'], hold_width=self.game_config['hold_width'],
                                  bg_color=self.game_config['track_color'], note_color=self.game_config['note_color'],
                                  hold_color=self.game_config['hold_color'], fall_time=self.fall_time)]

        self.score = 0

        self.bg_image = pg.image.load(os.path.join(beatmap_folder, self.metadata['Background']))
        bg_width, bg_height = self.bg_image.get_size()

        if bg_height * self.width >= bg_width * self.height:
            self.bg_image = pg.transform.scale(self.bg_image, (self.width, bg_height * self.width // bg_width))
        else:
            self.bg_image = pg.transform.scale(self.bg_image, (bg_width * self.height // bg_height, self.height))

    def render(self):
        self.surface.blit(self.bg_image, (0, 0))

        x_offset = (self.width -
                    self.track_count * (self.game_config['track_width'] + self.game_config['track_spacing']) +
                    self.game_config['track_spacing']) / 2

        for i in range(self.track_count):
            x = (self.game_config['track_width'] + self.game_config['track_spacing']) * i + x_offset
            self.tracks[i].render(self.surface, x, 0)

    def start(self):
        finished = False

        key_events = [(self.tracks[i].track_key, self.tracks[i].set_state) for i in range(self.track_count)]
        handler = EventHandler([(pg.QUIT, exit)], key_events)

        clock = pg.time.Clock()
        framerate = self.game_config['FPS']

        song = os.path.join(self.beatmap_folder, self.metadata['AudioFilename'])
        player = audioplayer.AudioPlayer(song)

        player.play()
        start_time = time.time() * 1000
        while not finished:

            current_time = time.time() * 1000
            for track in self.tracks:
                track.update_surface(current_time - start_time, self.hitobjects)

            self.render()
            handler.handle()

            pg.display.update()
            clock.tick(framerate)

        # Время, проведенное за игрой. Имеет смысл сохранять чтобы реализовать паузу.
        played_time = time.time() * 1000 - start_time


class EventHandler:
    def __init__(self, regular_events, key_events):
        """
        :param regular_events: Union(Union(pg.event, function)*). Выполняет function() при pg.event
        :param key_events: Union(Union(key, function)*). Выполняет function(key_state) если клавиша key зажата
        """

        self.regular_events_types = [regular_events[i][0] for i in range(len(regular_events))]
        self.regular_events_functions = [regular_events[i][1] for i in range(len(regular_events))]

        self.keys = [key_events[i][0] for i in range(len(key_events))]
        self.key_functions = [key_events[i][1] for i in range(len(key_events))]

    def handle(self):
        for event in pg.event.get():
            if event.type in self.regular_events_types:
                self.regular_events_functions[self.regular_events_types.index(event.type)]()

        key_states = pg.key.get_pressed()

        for i, key in enumerate(self.keys):
            self.key_functions[i](key_states[key])
