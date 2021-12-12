from Core.Game import *

FPS = 300

beatmaps = os.listdir('../Beatmaps/')

for i, beatmap in enumerate(beatmaps):
    print(f'{i}: {beatmap}')

beatmap_number = int(input('Select beatmap: '))
# beatmap_number = 3
difficulties = [i for i in os.listdir('../Beatmaps/' + beatmaps[beatmap_number]) if i.endswith('.osu')]

for i, difficulty in enumerate(difficulties):
    print(f'{i}: {difficulty}')

difficulty_number = int(input('Select difficulty: '))
# difficulty_number = 1
file = '../Beatmaps/' + beatmaps[beatmap_number] + '/' + difficulties[difficulty_number]
metadata = get_metadata(file)

mp3 = '../Beatmaps/' + beatmaps[beatmap_number] + '/' + metadata['AudioFilename']

hitobjects = get_hitobjects(file)

# track_count = int(metadata['CircleSize'])
# tracks = [Track(i, 'a', fall_time=1000) for i in range(track_count)]

pg.init()
screen = pg.display.set_mode((1600, 900))
clock = pg.time.Clock()

# player = audioplayer.AudioPlayer(mp3)
# player.play()

game = Game(screen, '../Beatmaps/' + beatmaps[beatmap_number], difficulties[difficulty_number])
game.start()
