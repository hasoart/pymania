import numpy as np
import os


def parse_hitobject(track_count, s):
    """
    Парсит строку с информацией об объекте в словарик
    :param track_count:
    Количество дорожек
    :param s:
    Строка с информацией вида "x,y,time,type,hitSound,endTime,hitSample"
    :return:
    Словарик с полями
    'x' - номер дорожки (начиная с 0)
    'time' - ожидаемое время нажатия объекта в мс
    'hitsound' - какой хитсаунд играть
    'type' - тип объекта note или hold
    'endTime' - (if type=hold) ожидаемое время отпускания холда в мс
    'score' - количество очков полученных за данную ноту (default -1)
    """

    object_params = list(s.strip().split(','))

    obj = dict()
    obj['x'] = int(round(int(object_params[0]) * track_count / 512 - 0.5))
    obj['time'] = int(object_params[2])
    obj['hitSound'] = int(object_params[4])

    type_flag = int(object_params[3])

    if type_flag & 0b00000001:
        obj['type'] = 'note'
    elif type_flag & 0b10000000:
        obj['type'] = 'hold'
        obj['endTime'] = int(object_params[5].split(':')[0])
    else:
        raise ValueError('Make Sure this is osu!mania map.')

    obj['score'] = -1

    return obj


def get_metadata(file):
    """
    Парсит метаданные заданной карты.

    :param file:
    путь к файлу карты
    :return:
    словарик с метаданными (числовые значения не переведены в float/int)
    (Секции [General], [Metadata], [Difficulty], Background из [Events])
    https://osu.ppy.sh/wiki/en/osu%21_File_Formats/Osu_%28file_format%29
    """
    with open(file, 'r') as f:
        data = f.readlines()
        metadata = dict()

        i = data.index('[General]\n') + 1
        while data[i] != '\n':
            key, val = data[i].split(':')
            metadata[key] = val.strip()
            i += 1

        i = data.index('[Metadata]\n') + 1
        while data[i] != '\n':
            key, val = data[i].split(':')
            metadata[key] = val.strip()
            i += 1

        i = data.index('[Difficulty]\n') + 1
        while data[i] != '\n':
            key, val = data[i].split(':')
            metadata[key] = val.strip()
            i += 1

        i = data.index('[Events]\n') + 1
        while data[i] != '\n':
            if not data[i].startswith('//'):
                event = data[i].split(',')

                if event[0] == event[1] == '0':
                    metadata['Background'] = event[2][1:-1]
                    break
            i += 1
        else:
            metadata['Background'] = None

        return metadata


def get_hitobjects(file):
    """
    Парсит объекты из файла карты.

    :param file:
    путь к файлу карты
    :return:
    Возвращает список всех объектов(в виде словарикв, см. parse_hitobjects) в хронологическом порядке
    """

    with open(file, 'r') as f:
        data = f.readlines()

        i = data.index('[Difficulty]\n') + 1
        while data[i] != '\n':
            key, val = data[i].split(':')
            if key == 'CircleSize':
                track_count = int(val)
                break
            i += 1

        i = data.index("[HitObjects]\n") + 1

        hitobjects = np.array(list(map(lambda x: parse_hitobject(track_count, x), data[i:])), dtype=object)

        return hitobjects


def get_beatmaps(beatmaps_folder):
    """

    :param beatmaps_folder: Папка с картами
    :return: Список со словариками с данными всех карт для отрисовки меню
    'beatmap_directory' - путь папки карты
    'artist' - Исполнитель песни
    'title' - название песни
    'music_path' - относительный путь до файла музыки
    'bg_image' - относительный путь до фонового изображения
    'diffs' - список с словариками вида {название сложности: название файла карты}
    """
    map_list = os.listdir(beatmaps_folder)
    beatmaps_list = []

    for map_ in map_list:
        map_dict = dict()

        map_directory = os.path.join(beatmaps_folder, map_)
        map_dict["beatmap_directory"] = map_directory

        beatmaps = [i for i in os.listdir(map_directory) if i.endswith('.osu')]

        if not beatmaps:
            continue

        metadata = get_metadata(os.path.join(map_directory, beatmaps[0]))

        map_dict['artist'] = metadata['Artist']
        map_dict['title'] = metadata['Title']

        map_dict['music_path'] = os.path.join(map_directory, metadata['AudioFilename'])
        map_dict['bg_image'] = os.path.join(map_directory, metadata['Background'])

        map_dict['diffs'] = []

        for beatmap in beatmaps:
            beatmap_path = os.path.join(map_directory, beatmap)
            metadata = get_metadata(beatmap_path)
            difficulty = metadata['Version']
            map_dict['diffs'].append({difficulty: beatmap})

        beatmaps_list.append(map_dict)

    return beatmaps_list
