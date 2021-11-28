import pygame as pg
import pygame.draw as draw
import time
import os
import audioplayer
from beatmap_parser import *
from track import Track

FPS = 300

beatmaps = os.listdir('../Beatmaps/')

for i, beatmap in enumerate(beatmaps):
    print(f'{i}: {beatmap}')

beatmap_number = int(input('Select beatmap: '))
difficulties = [i for i in os.listdir('../Beatmaps/' + beatmaps[beatmap_number]) if i.endswith('.osu')]

for i, difficulty in enumerate(difficulties):
    print(f'{i}: {difficulty}')

difficulty_number = int(input('Select difficulty: '))
file = '../Beatmaps/' + beatmaps[beatmap_number] + '/' + difficulties[difficulty_number]
metadata = get_metadata(file)

mp3 = '../Beatmaps/' + beatmaps[beatmap_number] + '/' + metadata['AudioFilename']

hitobjects = get_hitobjects(file)

track_count = int(metadata['CircleSize'])
tracks = [Track(i, 'a', fall_time=1000) for i in range(track_count)]

pg.init()
screen = pg.display.set_mode((100 * track_count, 800))
clock = pg.time.Clock()

player = audioplayer.AudioPlayer(mp3)
player.play()
start_time = time.time()
while True:
    screen.fill(0xffffff)
    curr_time = (time.time() - start_time) * 1000

    for i in range(track_count):
        tracks[i].update_surface(curr_time, hitobjects)
        tracks[i].render(screen, 100*i, 0)

    draw.rect(screen, 0xff0000, (0, 670, 100 * track_count, 30), 2)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit(0)

    pg.display.update()
    clock.tick(FPS)
