import time

import pygame as pg
import pygame.draw as draw


class Track:
    def __init__(self, track_number, track_key, width=100, height=800, note_height=30, hold_width=80, fall_time=5000,
                 bg_color=0xffffff, note_color=0x000000, hit_distance=100):
        self.track_number = track_number
        self.track_key = track_key

        self.width = width
        self.height = height
        self.note_height = note_height

        self.hold_width = hold_width
        self.hold_x = (width - hold_width) / 2

        self.bg_color = bg_color
        self.note_color = note_color

        self.hit_distance = hit_distance
        self.fall_time = fall_time

        self.surface = pg.Surface((width, height))

    def update_surface(self, current_time, hitobject_list):
        self.surface.fill(self.bg_color)

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

                draw.rect(self.surface, self.note_color, (0, y_start, self.width, self.note_height))
                draw.rect(self.surface, self.note_color, (0, y_end, self.width, self.note_height))

                draw.rect(self.surface, self.note_color,
                          (self.hold_x, y_end, self.hold_width, y_start - y_end + self.note_height))

    def get_surface(self):
        return self.surface

    def render(self, screen, x, y):
        screen.blit(self.surface, (x, y))

