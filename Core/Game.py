import time
import json
from typing import Tuple, Callable, Sequence

import pygame as pg
import audioplayer

from Utils.beatmap_utils import *
from Utils.Track import Track
from Settings.settings import settings


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


class ScoreMaster:
    """
    Класс для удобной работы с очками, их подсчета и хранения.
    """
    def __init__(self):
        self.score_list = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0

    def append(self, x: int) -> None:
        """
        Добавляет новые очки в список очков

        :param x: То, что добавляется в список. Допустимые значения - (300, 100, 50, 0, -1)
        :return: None
        """
        if x not in (-1, 0, 50, 100, 300):
            raise ValueError("Trying to append invalid value")

        if x >= 50:
            self.combo += 1
            self.score += x * self.combo
        else:
            self.combo = 0
        self.max_combo = max(self.combo, self.max_combo)
        self.score_list.append(x)

    def get_combo(self) -> int:
        """
        Возвращает текущее комбо
        :return: int
        """
        return self.combo

    def get_max_combo(self) -> int:
        """
        Возвращает максимальное комбо
        :return: int
        """
        return self.max_combo

    def get_score(self) -> int:
        """
        Возвращает текущие очки
        :return: int
        """
        return self.score

    def get_accuracy(self) -> float:
        """
        Возвращает текущую точность
        :return: float
        """
        return 100 * (sum(self.score_list) / (300 * len(self.score_list)) if self.score_list else 1.)

    def get_hit_counts(self) -> Tuple[int, int, int, int]:
        """
        Возвращает количество 300, 100, 50 и миссов

        :return: Количество 300, 100, 50 и миссов в виде (300, 100, 50, miss)
        """
        counts = [0, 0, 0, 0]

        for hit in self.score_list:
            if hit == 300:
                counts[0] += 1
            elif hit == 100:
                counts[1] += 1
            elif hit == 50:
                counts[2] += 1
            elif hit == 0:
                counts[3] += 1
            else:
                raise ValueError("Invalid value in score list")

        return tuple(counts)

    def get_rank(self) -> str:
        """
        Calculates the rank of player's result due to accuracy and having misses.

        :return: Rank of the score - 'SS' if accuracy is 100%,
                                     'S' if accuracy is greater than 93.333% and there are no misses,
                                     'A' if accuracy is greater than 93.333% but there are misses,
                                     'B' if accuracy is greater than 85%,
                                     'C' if accuracy is greater than 75%,
                                     'D' if accuracy is lower than 75%
        """
        accuracy = self.get_accuracy()
        have_misses = bool(self.get_hit_counts()[3])

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


class Game:
    def __init__(self, surface: pg.Surface, beatmap_folder: str, beatmap: str, system_to_return, volume: int = 50):
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

        self.tracks: list[Track] = []
        self.track_count = int(self.metadata['CircleSize'])
        self.fall_time = 1000

        self.system_to_return = system_to_return

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

    def start(self) -> None:
        """
        Начинает игру.
        :return: None
        """

        self.finished = False
        self.finished_early = False
        self.finished_score_screen = False
        # настройка обработчика событии
        key_events = [(self.tracks[i].track_key, self.tracks[i].set_state) for i in range(self.track_count)] + \
                     [(pg.K_ESCAPE, self.end_early)]
        handler = EventHandler([(pg.QUIT, exit)], key_events)

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

        if not self.finished_early:
            end_screen = self.stats()
            self.surface.blit(end_screen, (0, 0))
            while not self.finished_score_screen:
                handler.handle()

                pg.display.update()
                clock.tick(FPS)

        player.close()
        self.system_to_return.play(first_time=False)

    def stats(self) -> pg.Surface:
        """
        Returns the surface with players' game statistics
        """
        rank = self.score_master.get_rank()
        surface = pg.Surface((self.width, self.height))
        font_name = os.path.join(self.game_config['assets_directory'], 'PTMono-Regular.ttf')

        score = str(self.score_master.get_score())
        hit300, hit100, hit50, misses = map(str, self.score_master.get_hit_counts())
        max_combo = str(self.score_master.get_max_combo()) + 'x'
        accuracy = str(round(self.score_master.get_accuracy(), 2)) + '%'

        surface.blit(self.bg_image, (0, 0))

        inscriptions = [[120, 'Your Rank', (180, 0, 0), (900, 0)],
                [140, 'Score:', (180, 0, 0), (50, 0)],
                [140, score, (180, 0, 0), (380, 0)],
                [104, 'Your results', (180, 0, 0), (160, 100)],
                [80, ' 300  ', (180, 0, 0), (75, 180)],
                [80, ' 100  ', (180, 0, 0), (75, 255)],
                [80, ' 50  ', (180, 0, 0), (90, 330)],
                [80, 'misses', (180, 0, 0), (45, 405)],
                [80, hit300, (180, 0, 0), (400, 180)],
                [80, hit100, (180, 0, 0), (400, 255)],
                [80, hit50, (180, 0, 0), (400, 330)],
                [80, misses, (180, 0, 0), (400, 405)],
                [108, 'Max combo:', (180, 0, 0), (40, 490)],
                [112, max_combo, (180, 0, 0), (550, 490)],
                [108, 'Accuracy:', (180, 0, 0), (40, 595)],
                [112, accuracy, (180, 0, 0), (450, 595)]]

        for phrase in inscriptions:
            size, words, color, place = phrase
            f = pg.font.SysFont('ptmono', size)
            text = f.render(words, False, color)
            surface.blit(text, place)

        if rank == 'SS':
            f2 = pg.font.Font(font_name, 240)
            u_rank_text = f2.render(rank, False, (180, 0, 0))
            surface.blit(u_rank_text, (480, 80))
        else:
            f2 = pg.font.Font(font_name, 448)
            u_rank_text = f2.render(rank, False, (180, 0, 0))
            surface.blit(u_rank_text, (480, 60))

        return surface


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
