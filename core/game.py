import time
import json
import os
from typing import Tuple, Callable, Sequence

import pygame as pg
import audioplayer
import numpy as np

from utils.beatmap_utils import (
    get_metadata,
    get_hitobjects,
    get_map_duration
)
from utils.track import Track
from utils.ui_objects import stats
from utils.score_master import ScoreMaster
from settings.settings import settings


def get_objects_to_render(map_time: int, hitobjects: np.array, hitobject_count: int,
                          fall_time: int, render_start: int) -> Tuple[int, int]:
    """
    Возвращает какие ноты видны на экране, чтобы рендерить только их

    :param map_time: Время карты в мс
    :param hitobjects: np.array объектов
    :param hitobject_count: Количество объектов в списке hitobjeccts.
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


class Game:
    def __init__(self, surface: pg.Surface, beatmap_folder: str, beatmap: str, volume: int = 50):
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

        with open('./settings/game_config.json', 'r') as f:
            self.game_config = json.load(f)

        self.settings = settings

        self.score = 0
        self.score_master = ScoreMaster()

        self.tracks: list[Track] = []
        self.track_count = int(self.metadata['CircleSize'])
        self.fall_time = 1000

        self.exit = False

        for i in range(self.track_count):
            self.tracks += [Track(i, self.settings[f'{self.track_count}k_keys'][i], self.score_master,
                                  od=float(self.metadata['OverallDifficulty']),
                                  hit_distance=self.game_config['hit_distance'],
                                  width=self.game_config['track_width'], height=self.height,
                                  note_height=self.game_config['note_height'],
                                  hold_width=self.game_config['hold_width'],
                                  bg_color=self.game_config['track_color'], note_color=self.game_config['note_color'],
                                  hold_color=self.game_config['hold_color'], fall_time=self.fall_time,
                                  key_color=self.game_config['key_color'])]

        self.bg_image = pg.image.load(os.path.join(beatmap_folder, self.metadata['Background']))
        bg_width, bg_height = self.bg_image.get_size()

        if bg_height * self.width >= bg_width * self.height:
            self.bg_image = pg.transform.smoothscale(self.bg_image, (self.width, bg_height * self.width // bg_width))
        else:
            self.bg_image = pg.transform.smoothscale(self.bg_image, (bg_width * self.height // bg_height, self.height))

        self.combo_font = pg.font.Font(os.path.join(self.game_config['assets_directory'], 'PTMono-Regular.ttf'), 70)
        self.accuracy_font = pg.font.Font(os.path.join(self.game_config['assets_directory'], 'PTMono-Regular.ttf'), 30)

        self.finished = False
        self.finished_early = False
        self.finished_score_screen = False

    def render(self) -> None:
        """
        Рендерит игру
        :return: None
        """
        x_offset = (self.width -
                    self.track_count * (self.game_config['track_width'] + self.game_config['track_spacing']) +
                    self.game_config['track_spacing']) / 2

        for i in range(self.track_count):
            x = (self.game_config['track_width'] + self.game_config['track_spacing']) * i + x_offset
            self.tracks[i].render(self.surface, x, 0)

        score_surface = self.combo_font.render(f'{self.score_master.get_score()}', True, (255, 255, 255))
        w, h = score_surface.get_size()
        self.surface.blit(self.bg_image, (self.width - w - 20, 20), (self.width - w - 20, 20, w, h))
        self.surface.blit(score_surface, (self.width - w - 20, 20))

        accuracy_surface = self.accuracy_font.render(f'{self.score_master.get_accuracy():.2f}%', True, (255, 255, 255))
        w1, h1 = self.accuracy_font.size('100.00%')
        w2, h2 = accuracy_surface.get_size()
        self.surface.blit(self.bg_image, (self.width - w1 - 20, 40 + h), (self.width - w1 - 20, 40 + h, w1, h1))
        self.surface.blit(accuracy_surface, (self.width - w2 - 20, 40 + h))

        combo_surface = self.combo_font.render(f'{self.score_master.get_combo()}x', True, (255, 255, 255))
        w, h = self.combo_font.size(f'{self.score_master.get_max_combo()}x')
        self.surface.blit(self.bg_image, (20, self.height - h - 20),
                          (20, self.height - h - 20, w, h))
        self.surface.blit(combo_surface, (20, self.height - h - 20))

    def end_early(self, key_state: int) -> None:
        """
        Функция, которая активизируется если игрок хочет досрочно закончить игру.
        :param key_state:
        :return: None
        """

        if key_state == 1:
            if not self.finished:
                self.finished_early = self.finished = self.finished_score_screen = True
            elif self.finished and not self.finished_early:
                self.finished_score_screen = True

    def exit_game(self):
        """
        Меняет флажок sself.exit на true, что приводит к завершению игры.
        :return:
        """
        self.exit = True

    def start(self) -> int:
        """
        Начинает игру.
        :return: 0 если игра закончиоась натуральным ходом, -1 если игрок нажал на "закрыть окно" в системе.
        """

        # настройка обработчика событии
        key_events = [(self.tracks[i].track_key, self.tracks[i].set_state) for i in range(self.track_count)] + \
                     [(pg.K_ESCAPE, self.end_early)]
        handler = EventHandler([(pg.QUIT, self.exit_game)], key_events)

        # Импортирование музыки
        song = os.path.join(self.beatmap_folder, self.metadata['AudioFilename'])
        player = audioplayer.AudioPlayer(song)
        player.volume = self.volume

        render_start = 0
        FPS = self.game_config['FPS']
        clock = pg.time.Clock()
        map_duration = get_map_duration(self.hitobjects)
        music_started = False

        # Если карта начинается слишком быстро, создает задержку для удобства.
        if self.hitobjects[0]['time'] < 2000:
            time_correction = 2000 - self.hitobjects[0]['time']
        else:
            time_correction = 0

        self.surface.blit(self.bg_image, (0, 0))

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

            if self.exit:
                return -1

        if not self.finished_early:
            end_screen = stats(self)
            self.surface.blit(end_screen, (0, 0))
            while not self.finished_score_screen:
                handler.handle()

                pg.display.update()
                clock.tick(FPS)

                if self.exit:
                    return -1

        player.close()

        return 0


class EventHandler:
    """
    Класс для обработки событии.
    """

    def __init__(self, regular_events: Sequence[Tuple[int, Callable]],
                 key_events: Sequence[Tuple[int, Callable]]) -> None:
        """
        :param regular_events: Tuple[Tuple[pg.event, Callable]] Выполняет Callable() при pg.event.Event
        :param key_events: Tuple[Tuple[key: int, Callable]] Выполняет Callable(key_state) если клавиша key зажата
        """

        self.regular_events_types: [int] = [regular_events[i][0] for i in range(len(regular_events))]
        self.regular_events_functions: [Callable] = [regular_events[i][1] for i in range(len(regular_events))]

        self.keys: [int] = [key_events[i][0] for i in range(len(key_events))]
        self.key_functions: [Callable] = [key_events[i][1] for i in range(len(key_events))]

    def handle(self) -> None:
        """
        Обрабатывает события.
        :return: None
        """
        for event in pg.event.get():
            if event.type in self.regular_events_types:
                self.regular_events_functions[self.regular_events_types.index(event.type)]()

        key_states = pg.key.get_pressed()

        for i, key in enumerate(self.keys):
            self.key_functions[i](key_states[key])
