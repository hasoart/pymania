import time

import pygame as pg
import pygame.draw as draw


class Track:
    def __init__(self, track_number, track_key, score_list, width=100, height=800, note_height=30, hold_width=80, fall_time=1000,
                 bg_color=0xffffff, note_color=0x000000, hold_color=0x000000, key_color=(0x800406, 0xe10509),
                 hit_distance=100):
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
        :param note_color: Цвет нот
        :param hold_color: Цвет тонкой части холда
        :param key_color: Union(Color, Color). Цвета клавишы при ненажатом и нажатом состояниях
        :param hit_distance: Высота точки нажатия измеряя от нижней части дорожки
        """
        self.track_number = track_number
        self.track_key = track_key
        self.score_list = score_list

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

    def update_surface(self, current_time, hitobject_list):
        """
        Обновляет дорожку

        :param current_time: Текущее время карты в мс
        :param hitobject_list: Список объектов которые будуд рендерится
        :return: None
        """
        self.surface.fill(self.bg_color)

        draw.line(self.surface, 0xaaaaaa, (0, self.height - self.hit_distance - self.note_height),
                  (self.width, self.height - self.hit_distance - self.note_height), 3)

        for hitobject in hitobject_list:
            if hitobject['x'] != self.track_number:
                continue

            if hitobject['type'] == 'note':
                y = (current_time - hitobject['time'] + self.fall_time) * (self.height - self.hit_distance) \
                    / self.fall_time - self.note_height

                draw.rect(self.surface, self.note_color, (0, y, self.width, self.note_height))
            elif hitobject['type'] == 'hold':
                y_start = (current_time - hitobject['time'] + self.fall_time) * (self.height - self.hit_distance) \
                          / self.fall_time - self.note_height

                y_end = (current_time - hitobject['endTime'] + self.fall_time) * (self.height - self.hit_distance) \
                    / self.fall_time - self.note_height

                draw.rect(self.surface, self.hold_color,
                          (self.hold_x, y_end, self.hold_width, y_start - y_end + self.note_height))

                draw.rect(self.surface, self.note_color, (0, y_start, self.width, self.note_height))
                draw.rect(self.surface, self.note_color, (0, y_end, self.width, self.note_height))

        draw.rect(self.surface, self.key_color[self.state],
                  (0, self.height - self.hit_distance, self.width, self.hit_distance))

        self.last_state = self.state

    def set_state(self, state):
        self.state = state

    def get_surface(self):
        """
        Возвращает поверхность дорожки
        :return: Поверхность дорожки
        """
        return self.surface

    def render(self, screen, x, y):
        """
        Рендерит дорожку на screen в точке (x, y)

        :param screen: Поверхность на которую будем рендерить
        :param x: координата x на screen
        :param y: координата y на screen

        :return: None
        """
        screen.blit(self.surface, (x, y))
