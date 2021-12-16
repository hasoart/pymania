import time
import json

import pygame as pg
import audioplayer

from Utils.beatmap_utils import *
from Utils.Track import Track
from Settings.settings import settings


def get_objects_to_render(map_time, hitobjects, hitobject_count, fall_time, render_start):
    """
    Возвращает какие ноты видны на экране, чтобы рендерить только их

    :param map_time: Время карты в мс
    :param hitobjects: Список или np.array объектов
    :param hitobject_count: Количество объектов в списке hitobjeccts
    :param render_start: Предыдущее значение начала рендера
    :param fall_time: Время падения ноты от края до края

    :return: render_start, render_end - индексы, показывающие какие элементы рендерить
    """
    new_render_start = render_start

    while True:
        if hitobjects[new_render_start]['type'] == 'note':
            obj_time = hitobjects[new_render_start]['time']
        else:
            obj_time = hitobjects[new_render_start]['endTime']
        if obj_time >= map_time - 1000 or new_render_start == hitobject_count - 1:
            break
        new_render_start += 1

    i = new_render_start
    while True:
        if hitobjects[i]['time'] >= map_time + 1000 + fall_time or i == hitobject_count - 1:
            break
        i += 1
    render_end = i + 1

    return new_render_start, render_end


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


class Game:
    def __init__(self, surface, beatmap_folder, beatmap, system_to_return, volume=50):
        """
        :param surface: Поверхность игры
        :param beatmap_folder: путь директории карты
        :param beatmap: имя карты (путь относительно beatmap)
        :param volume: громкость
        """

        self.surface = surface
        self.beatmap_folder = beatmap_folder
        self.beatmap = os.path.join(beatmap_folder, beatmap)
        self.volume = volume

        self.metadata = get_metadata(self.beatmap)
        self.hitobjects = get_hitobjects(self.beatmap)
        self.hitobject_count = len(self.hitobjects)

        self.width, self.height = surface.get_size()

        with open('./Settings/game_config.json', 'r') as f:
            self.game_config = json.load(f)

        self.settings = settings

        self.score = 0
        self.score_master = ScoreMaster()

        self.tracks = []
        self.track_count = int(self.metadata['CircleSize'])
        self.fall_time = 1000

        self.system_to_return = system_to_return

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

    def end_early(self, key_state):
        if key_state == 1:
            self.finished_early = self.finished = True

    def start(self):
        self.finished = False
        self.finished_early = False

        key_events = [(self.tracks[i].track_key, self.tracks[i].set_state) for i in range(self.track_count)] + \
                     [(pg.K_ESCAPE, self.end_early)]
        handler = EventHandler([(pg.QUIT, exit)], key_events)

        clock = pg.time.Clock()
        FPS = self.game_config['FPS']

        song = os.path.join(self.beatmap_folder, self.metadata['AudioFilename'])
        player = audioplayer.AudioPlayer(song)
        player.volume = self.volume

        render_start = 0

        self.surface.blit(self.bg_image, (0, 0))

        map_duration = get_map_duration(self.hitobjects)

        # if map starts to abruptly give player some time
        if self.hitobjects[0]['time'] < 3000:
            time_correction = 3000 - self.hitobjects[0]['time']
        else:
            time_correction = 0

        music_started = False

        start_time = time.time() * 1000

        while not self.finished:
            current_time = time.time() * 1000
            map_time = current_time - start_time - time_correction

            if (not music_started) and map_time >= 0:
                player.play()
                music_started = True

            render_start, render_end = get_objects_to_render(map_time, self.hitobjects, self.hitobject_count,
                                                             self.fall_time, render_start)

            for track in self.tracks:
                track.update(map_time, self.hitobjects[render_start:render_end])
            self.render()
            handler.handle()

            pg.display.update()
            clock.tick(FPS)

            if map_time >= map_duration + 3000:
                self.finished = True

        player.close()
        self.system_to_return.play(first_time=False)

    def define_rank(self):
        """
        Calculates the rank of player's result due to accuracy and having misses
        """
        accuracy = self.score_master.get_accuracy()
        have_misses = False  # FIXME -- waiting for the function

        if accuracy == 100:
            rank = 'SS'
        elif accuracy >= 93.333:
            if not have_misses:
                rank = 'S'
            else:
                rank = 'A'
        elif accuracy >= 85:
            rank = 'B'
        elif accuracy >= 75:
            rank = 'C'
        else:
            rank = 'D'

        return rank

    def stats(self):
        """
        Returns the surface with players' game statisctics
        """
        rank = self.define_rank()
        surface = pg.Surface((1400, 700))

        frame = pg.image.load('./assets/bg.jpg')
        frame_rect = frame.get_rect(topleft=(0, 0))
        surface.blit(frame, frame_rect)

        f1 = pg.font.SysFont('ptmono', 48)
        u_rank_text = f1.render('Your Rank', False, (180, 0, 0))
        surface.blit(u_rank_text, (500, 0))

        if rank == 'SS':
            f2 = pg.font.SysFont('ptmono', 240)
            u_rank_text = f2.render(rank, False, (180, 0, 0))
            surface.blit(u_rank_text, (480, 80))
        else:
            f2 = pg.font.SysFont('ptmono', 448)
            u_rank_text = f2.render(rank, False, (180, 0, 0))
            surface.blit(u_rank_text, (480, 60))

        return surface



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
