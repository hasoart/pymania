import os
import time
import json

import pygame as pg
import pygame.draw as draw
import audioplayer

from beatmap_parser import *
from settings import settings
from Track import Track


class ScoreMaster:
    def __init__(self):
        self.score_list = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0

    def append(self, x):
        if x >= 50:
            self.combo += 1
            self.score += x * self.combo
        else:
            self.max_combo = max(self.combo, self.max_combo)
            self.combo = 0
        self.score_list.append(x)

    def get_combo(self):
        return self.combo

    def get_max_combo(self):
        return self.max_combo

    def get_score(self):
        return self.score

    def get_accuracy(self):
        return 100 * (sum(self.score_list) / (300 * len(self.score_list)) if self.score_list else 1.)


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
        self.hitobject_count = len(self.hitobjects)

        self.width, self.height = surface.get_size()

        with open('game_config.json', 'r') as f:
            self.game_config = json.load(f)

        self.settings = settings

        self.score = 0
        self.score_master = ScoreMaster()

        self.tracks = []

        self.track_count = int(self.metadata['CircleSize'])
        self.fall_time = 1000

        for i in range(self.track_count):
            self.tracks += [Track(i, self.settings[f'{self.track_count}k_keys'][i], self.score_master,
                                  od=float(self.metadata['OverallDifficulty']),
                                  hit_distance=self.game_config['hit_distance'],
                                  width=self.game_config['track_width'], height=self.height,
                                  note_height=self.game_config['note_height'], hold_width=self.game_config['hold_width'],
                                  bg_color=self.game_config['track_color'], note_color=self.game_config['note_color'],
                                  hold_color=self.game_config['hold_color'], fall_time=self.fall_time,
                                  key_color=self.game_config['key_color'])]

        self.bg_image = pg.image.load(os.path.join(beatmap_folder, self.metadata['Background']))
        bg_width, bg_height = self.bg_image.get_size()

        if bg_height * self.width >= bg_width * self.height:
            self.bg_image = pg.transform.smoothscale(self.bg_image, (self.width, bg_height * self.width // bg_width))
        else:
            self.bg_image = pg.transform.smoothscale(self.bg_image, (bg_width * self.height // bg_height, self.height))

        self.big_font = pg.font.Font(os.path.join(self.game_config['assets_directory'], 'PTMono-Regular.ttf'), 70)
        self.small_font = pg.font.Font(os.path.join(self.game_config['assets_directory'], 'PTMono-Regular.ttf'), 30)

    def render(self):
        x_offset = (self.width -
                    self.track_count * (self.game_config['track_width'] + self.game_config['track_spacing']) +
                    self.game_config['track_spacing']) / 2

        for i in range(self.track_count):
            x = (self.game_config['track_width'] + self.game_config['track_spacing']) * i + x_offset
            self.tracks[i].render(self.surface, x, 0)

        score_surface = self.big_font.render(f'{self.score_master.get_score()}', True, (255, 255, 255))
        w, h = score_surface.get_size()
        self.surface.blit(self.bg_image, (self.width - w - 20, 20), (self.width - w - 20, 20, w, h))
        self.surface.blit(score_surface, (self.width - w - 20, 20))

        accuracy_surface = self.small_font.render(f'{self.score_master.get_accuracy():.2f}%', True, (255, 255, 255))
        max_acc_surface = self.small_font.render('100.00%', True, (255, 255, 255))
        w1, h1 = max_acc_surface.get_size()
        w2, h2 = accuracy_surface.get_size()
        self.surface.blit(self.bg_image, (self.width - w1 - 20, 40 + h), (self.width - w1 - 20, 40 + h, w1, h1))
        self.surface.blit(accuracy_surface, (self.width - w2 - 20, 40 + h))

        combo_surface = self.big_font.render(f'{self.score_master.get_combo()}x', True, (255, 255, 255))
        max_combo_surface = self.big_font.render(f'{self.score_master.get_max_combo()}x', True, (255, 255, 255))
        w, h = max_combo_surface.get_size()[0], combo_surface.get_size()[1]
        self.surface.blit(self.bg_image, (20, self.height - h - 20),
                          (20, self.height - h - 20, w, h))
        self.surface.blit(combo_surface, (20, self.height - h - 20))

    def start(self):
        finished = False

        key_events = [(self.tracks[i].track_key, self.tracks[i].set_state) for i in range(self.track_count)]
        handler = EventHandler([(pg.QUIT, exit)], key_events)

        clock = pg.time.Clock()
        FPS = self.game_config['FPS']

        song = os.path.join(self.beatmap_folder, self.metadata['AudioFilename'])
        player = audioplayer.AudioPlayer(song)

        render_start = 0

        player.play()
        start_time = time.time() * 1000
        self.surface.blit(self.bg_image, (0, 0))

        while not finished:
            current_time = time.time() * 1000
            map_time = current_time - start_time

            # Считает какие ноты видны, чтобы рендерить только их
            while True:
                if self.hitobjects[render_start]['type'] == 'note':
                    obj_time = self.hitobjects[render_start]['time']
                else:
                    obj_time = self.hitobjects[render_start]['endTime']
                if obj_time >= map_time - 1000 or render_start == self.hitobject_count - 1:
                    break
                render_start += 1

            i = render_start
            while True:
                if self.hitobjects[i]['time'] >= map_time + 1000 + self.fall_time or i == self.hitobject_count - 1:
                    break
                i += 1
            render_end = i + 1

            for track in self.tracks:
                track.update(map_time, self.hitobjects[render_start:render_end])
            self.render()
            handler.handle()

            pg.display.update()
            clock.tick(FPS)


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
