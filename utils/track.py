from typing import Tuple, Union, List

import numpy as np
import pygame as pg
import pygame.draw as draw

from utils.score_master import ScoreMaster


def get_hit_windows(od: float) -> Tuple[float, float, float]:
    """
    Считает рамки очков по времени
    :param od: Overal Difficulty карты
    :return: window_300, windows_100, window_50
    """
    window_50 = 400 - 20 * od
    windows_100 = 280 - 16 * od
    window_300 = 160 - 12 * od
    return window_300, windows_100, window_50


class Track:
    """
    Класс дорожки. Используется для удобной работы с дорожками.
    """
    def __init__(self, track_number: int, track_key: int, score_list: Union[List, ScoreMaster],
                 od: float = 5., width: int = 100, height: int = 800, note_height: int = 30, hold_width: int = 80,
                 fall_time: int = 1000,
                 bg_color: Union[int, Tuple[int, int, int]] = 0xffffff,
                 note_color: Tuple[Union[int, Tuple[int, int, int]], Union[int, Tuple[int, int, int]]]
                 = (0xff0000, 0x000000), hold_color: Union[int, Tuple[int, int, int]] = 0x000000,
                 key_color: Tuple[Union[int, Tuple[int, int, int]], Union[int, Tuple[int, int, int]]]
                 = (0x800406, 0xe10509), hit_distance: int = 100):
        """
        :param track_number: Номер дорожки
        :param track_key: Клавиша дорожки
        :param score_list: Список хранящий очки за нажатия
        :param width: Ширина дорожки
        :param height: Высота дорожки
        :param note_height: Высота нот
        :param hold_width: Ширина тонкой части холда
        :param fall_time: Время в мс за которое нота проходит от начала дорожки до точки нажатия
        :param bg_color: Цвет дорожки
        :param note_color: Union(Color, Color). Цвета нот
        :param hold_color: Union(Color, Color). Цвета тонкой части холда
        :param key_color: Union(Color, Color). Цвета клавишы
        :param hit_distance: Высота точки нажатия измеряя от нижней части дорожки
        """
        self.track_number = track_number
        self.track_key = track_key
        self.score_list = score_list

        self.window_300, self.window_100, self.window_50 = get_hit_windows(od)

        self.width = width
        self.height = height
        self.note_height = note_height

        self.hold_width = hold_width
        self.hold_x = (width - hold_width) / 2

        self.bg_color = bg_color
        self.note_color = note_color
        self.hold_color = hold_color
        self.key_color = key_color

        self.hit_distance = hit_distance
        self.fall_time = fall_time

        self.state = 0
        self.last_state = 0

        self.surface = pg.Surface((width, height))

        key_name = pg.key.name(self.track_key)
        key_font = pg.font.Font('./assets/PTMono-Regular.ttf', hit_distance // 10)
        self.key_name_surface = key_font.render(key_name, True, (128, 128, 128))

    def get_score(self, time_diff: int) -> int:
        """
        Calculates the score for a given press
        :param time_diff: current_time - hit_time
        :return: Score earned for that hit
        """
        if time_diff > self.window_50:
            return 0
        elif time_diff < -self.window_50:
            return -1
        elif self.window_50 >= abs(time_diff) > self.window_100:
            return 50
        elif self.window_100 >= abs(time_diff) > self.window_300:
            return 100
        elif self.window_300 >= abs(time_diff):
            return 300

    def update(self, current_time: int, hitobject_list: Union[np.array, List]) -> None:
        """
        Обновляет дорожку

        :param current_time: Текущее время карты в мс
        :param hitobject_list: Список объектов которые будут рендерится
        :return: None
        """
        self.surface.fill(self.bg_color)

        # Линия сверху клавиш
        draw.line(self.surface, 0xaaaaaa, (0, self.height - self.hit_distance - self.note_height),
                  (self.width, self.height - self.hit_distance - self.note_height), 3)

        # press 1 если зажатие, 0 если ничего, -1 если отпускание
        if self.last_state != self.state:
            press = 1 if self.state == 1 else -1
        else:
            press = 0

        for hitobject in hitobject_list:
            if hitobject['x'] != self.track_number:
                continue

            time_diff = current_time - hitobject['time']
            if hitobject['type'] == 'note':
                score = self.get_score(time_diff)
                if score == 0 and hitobject['score'] == -1:
                    hitobject['score'] = 0
                    self.score_list.append(0)
                if press == 1:
                    if hitobject['score'] == -1:
                        if score == -1:
                            press = 0
                        elif score >= 50:
                            hitobject['score'] = score
                            self.score_list.append(score)
                            press = 0
            else:
                start_score = self.get_score(time_diff)
                if start_score == 0 and hitobject['score'] == -1:
                    hitobject['score'] = 0
                    self.score_list.append(0)
                if press == 1:
                    if hitobject['score'] == -1:
                        if start_score == -1:
                            press = 0
                        elif start_score >= 50:
                            hitobject['score'] = 1  # 1 means it is being held
                            press = 0
                if press == -1:
                    end_score = self.get_score(current_time - hitobject['endTime'])
                    if hitobject['score'] == 1:
                        if end_score != -1:
                            hitobject['score'] = end_score
                            self.score_list.append(end_score)
                            press = 0
                        elif end_score == -1:
                            hitobject['score'] = 0
                            self.score_list.append(0)
                            press = 0

            if hitobject['type'] == 'note':
                y = (current_time - hitobject['time'] + self.fall_time) * (self.height - self.hit_distance) \
                    / self.fall_time - self.note_height

                note_color = self.note_color[hitobject['score'] != -1]

                draw.rect(self.surface, note_color, (0, y, self.width, self.note_height))

            elif hitobject['type'] == 'hold':
                y_start = (current_time - hitobject['time'] + self.fall_time) * (self.height - self.hit_distance) \
                    / self.fall_time - self.note_height

                y_end = (current_time - hitobject['endTime'] + self.fall_time) * (self.height - self.hit_distance) \
                    / self.fall_time - self.note_height

                note_color = self.note_color[hitobject['score'] != -1]
                hold_color = self.hold_color[hitobject['score'] != -1]
                draw.rect(self.surface, hold_color,
                          (self.hold_x, y_end, self.hold_width, y_start - y_end + self.note_height))

                draw.rect(self.surface, note_color, (0, y_start, self.width, self.note_height))
                draw.rect(self.surface, note_color, (0, y_end, self.width, self.note_height))

        # Клавиша
        draw.rect(self.surface, self.key_color[self.state],
                  (0, self.height - self.hit_distance, self.width, self.hit_distance))

        w, h = self.key_name_surface.get_size()
        x = (self.width - w) // 2
        y = self.height - self.hit_distance + (self.hit_distance - h) // 2
        self.surface.blit(self.key_name_surface, (x, y))

        self.last_state = self.state

    def set_state(self, state: Union[int, bool]) -> None:
        self.state = state

    def get_surface(self) -> pg.Surface:
        """
        Возвращает поверхность дорожки
        :return: Поверхность дорожки
        """
        return self.surface

    def render(self, screen: pg.Surface, x: int, y: int) -> None:
        """
        Рендерит дорожку на screen в точке (x, y)

        :param screen: Поверхность на которую будем рендерить
        :param x: координата x на screen
        :param y: координата y на screen

        :return: None
        """
        screen.blit(self.surface, (x, y))
