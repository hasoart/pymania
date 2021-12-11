# coding:utf-8
import pygame
import os
import pathlib
import json
from GameMaster import GameMaster
from beatmap_parser import get_beatmaps

pygame.font.init()
pygame.mixer.init()


class TextBox:
    # class textbox
    def __init__(self, position, font, font_color, text, aligment, bg_image=None, box_size=(1.2, 1.2), size=None):
        """
        init for class Textbox
        position - cords of left high corner or center
        font - size of font
        font_color - color of text
        text - text
        aligment - 'center': position - cords of center
                   'left': position - cords of left high corner
        bg_image - image in background of text
        box_size - ratio of the size of rect to size of text
        size - size of textbox
        """
        self.position = position
        self.bg_image = bg_image
        self.font = font
        self.font_color = font_color
        self.text = text
        self.aligment = aligment
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)

        if size:
            self.size = size
        else:
            # count size based on size of text:
            self.size = (int(text_surface.get_width() * box_size[0]), int(text_surface.get_height() * box_size[1]))
        if self.aligment == 'center':
            self.position = [self.position[0] - self.size[0] / 2, self.position[1] - self.size[1] / 2]
        # get background surface
        if self.bg_image:
            rect_surface = pygame.image.load(self.bg_image).convert_alpha()
            self.rect_surface = pygame.transform.smoothscale(rect_surface, self.size)
        else:
            self.rect_surface = None

    def get_surface(self):
        # get surface of drawing textbox
        # draw background image:
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        if self.rect_surface:
            surface.blit(self.rect_surface, (0, 0))

        # write text
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)
        text_rect = text_surface.get_rect(center=(self.size[0] / 2, self.size[1] / 2))
        surface.blit(text_surface, text_rect)

        return surface


class Button(TextBox):
    def __init__(self, position, font, font_color, text, aligment, bg_image, func, box_size=(1.2, 1.2), size=None):
        """
        init for class Button
        position - cords of left high corner or center
        font - size of font
        font_color - color of text
        text - text
        aligment - 'center': position - cords of center
                   'left': position - cords of left high corner
        bg_image - image in background of text
        func - what to do if button is clicked
        box_size - ratio of the size of rect to size of text
        size - size of Button
        """
        super().__init__(position, font, font_color, text, aligment, bg_image, box_size, size)
        self.func = func

    def click(self, event):
        """
        reaction for events:
        do func if clicked
        event - pygame Event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            rho = [event.pos[0] - self.position[0], event.pos[1] - self.position[1]]
            if self.size[0] >= rho[0] >= 0 and self.size[1] >= rho[1] >= 0:
                self.func()


class Slider:
    def __init__(self, position, image, on_color, off_color, size, system, name, font, font_color, value=0.5,
                 circle_scale=1.3):
        """
        init for class Slider (Polzunok)
        position - coords of left high corner
        image - image of circle
        on_color - color of part of rect before circle
        off_color - color of part of rect after circle
        size - size of slider
        system - system of game objects (System)
        name - name of slider
        font - size of font
        font_color - color of text
        value - fraction of part of rect before circle and all rect
        circle_scale - ratio of y_size of slider to radius of circle
        """
        self.position = position
        self.image = image
        self.on_color = on_color
        self.off_color = off_color
        self.size = size
        self.value = value
        self.condition = False
        self.system = system
        self.name = name
        self.font = font
        self.font_color = font_color
        self.circle_scale = circle_scale
        # count circle_size and pos based on value, size and position
        self.circle_size = (int(self.size[1] * self.circle_scale), int(self.size[1] * self.circle_scale))
        self.circle_pos = (self.position[0] + self.size[0] * self.value, self.position[1] + self.circle_size[1] / 2)
        # get surface of circle:
        self.circle_surface = pygame.image.load(self.image).convert_alpha()
        self.circle_surface = pygame.transform.smoothscale(self.circle_surface, self.circle_size)
        self.circle_surface.set_colorkey((253, 253, 253))

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_surface(self):
        # get surface of drawing textbox
        ratio = self.system.constants['settings'][self.name + '_value']
        # draw background image:

        # draw text:
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(str(round(self.value, 2)), True, self.font_color)
        surface = pygame.Surface(
            (self.size[0] * self.circle_scale, self.size[1] * ratio[1] + text_surface.get_height()),
            pygame.SRCALPHA,
            32)
        surface.blit(text_surface, (
            self.size[0] / 2 - text_surface.get_width() / 2, ratio[1] * self.size[1] - text_surface.get_height() / 2))
        # draw rects:
        pygame.draw.rect(surface, self.on_color,
                         ((0, self.size[1] * (self.circle_scale - 1) / 2), (self.size[0] * self.value, self.size[1])))
        pygame.draw.rect(surface, self.off_color, (
            (self.size[0] * self.value, self.size[1] * (self.circle_scale - 1) / 2),
            (self.size[0] * (1 - self.value), self.size[1])))
        # draw circle:
        surface.blit(self.circle_surface, (self.size[0] * self.value - self.circle_size[0] / 2, 0))

        return surface

    def click(self, event):
        """
        reaction for events
        event - pygame Event
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # change status of object if button clicked
            rho = (event.pos[0] - self.circle_pos[0], event.pos[1] - self.circle_pos[1])
            if rho[0] ** 2 + rho[1] ** 2 <= (self.circle_size[1] / 2) ** 2:
                self.condition = True

        if event.type == pygame.MOUSEMOTION and self.condition:
            # change position of circle and value
            if self.size[0] - self.circle_size[0] / 2 >= event.pos[0] - self.position[0] >= self.circle_size[0] / 2:
                self.value = (event.pos[0] - self.position[0] - self.circle_size[0] / 2) / (
                        self.size[0] - self.circle_size[0])
                self.circle_pos = (
                    self.position[0] + self.size[0] * self.value, self.position[1] + self.circle_size[1] / 2)
                system.set(self.name, self.value)

        if event.type == pygame.MOUSEBUTTONUP and self.condition:
            # change condition of object if clicked
            self.condition = False


class DropDown:
    def __init__(self, position, image, font, font_color, objects, constants, system, rect_pos, main_size=None):
        """
        :param position: pos of left high corner of main block
        :param image: image of arrow
        :param font: font of text
        :param font_color: colour of text
        :param objects: [{'text':'', 'type':main/not_main, 'func':func, 'bg_image':bg_image},...,]
        :param constants: constants of game like screen or file with data
        :param system: system of current game
        :param rect_pos: position of left corner of opening rectangle with information about song
        :param main_size: size of one block
        """
        self.position = position
        self.image = image
        self.font = font
        self.font_color = font_color
        self.objects = objects
        self.drawing_objects = []
        self.size = ()
        self.additional_objects = []
        self.constants = constants
        self.system = system
        self.screen = self.system.screen
        self.rect_pos = rect_pos
        self.add_obj_func = {}
        # count font of text if main_size:
        max_size = [0, 0]
        if main_size:
            # change font if no freedom space
            for obj in self.objects:
                f = pygame.font.Font(None, self.font)
                text_surface = f.render(obj['text'], True, self.font_color)
                max_size[0] = max(max_size[0], int(text_surface.get_size()[0] * constants['box_size'][0]))
                max_size[1] = max(max_size[1], int(text_surface.get_size()[1] * constants['box_size'][1]))
            self.font = min(int(self.font * main_size[0] / max_size[0]), int(self.font * main_size[1] / max_size[1]))

        # add objects into list to drawing objects
        for obj in self.objects:
            if obj['type'] == 'main':
                # add main block:
                main = TextBox((0, 0), self.font, self.font_color, obj['text'], 'left', obj['rect_image'],
                               size=main_size)
                arrow = Button((main.size[0], 0), self.font, self.font_color,
                               '', 'left', self.image, (self.unlock, self.lock), size=(main.size[1], main.size[1]))
                self.drawing_objects.append(main)
                self.drawing_objects.append(arrow)
                self.arrow = arrow
                self.main = main
                self.main_obj = obj
            else:
                # add not main blocks
                button = Button(
                    (int((self.main.size[0] + self.arrow.size[0]) * self.constants['start']['indent']),
                     self.main.size[1] * (len(self.additional_objects) + 1)),
                    self.font, self.font_color, obj['text'], 'left', obj['rect_image'], self.click,
                    size=(int((self.main.size[0] + self.arrow.size[0]) * (1 - self.constants['start']['indent'])),
                          self.main.size[1]))
                self.additional_objects.append(button)
                self.add_obj_func[button] = obj
                self.opened = False
                self.size = (self.main.size[0] + self.arrow.size[0], self.main.size[1] * len(self.objects))

    def unlock(self):
        """ when list is close and became into opened:"""
        self.drawing_objects += self.additional_objects
        constants = self.system.constants['drop_down']
        # add rectangle with information about current song:
        name = TextBox(
            self.rect_pos,
            self.font, self.font_color, 'Title: ' + self.main_obj['title'], 'left', self.main_obj['rect_image'],
            size=(int(constants['title_size'][0] * self.system.screen.get_width()),
                  int(constants['title_size'][1] * self.system.screen.get_height())))
        artist = TextBox(
            (self.rect_pos[0], self.rect_pos[1] + name.size[1]),
            self.font, self.font_color, 'Artist: ' + self.main_obj['artist'], 'left', self.main_obj['rect_image'],
            size=(int(constants['title_size'][0] * self.system.screen.get_width()),
                  int(constants['title_size'][1] * self.system.screen.get_height())))
        rect = TextBox(
            (self.rect_pos[0], self.rect_pos[1] + name.size[1] + artist.size[1]),
            self.font, self.font_color, '', 'left', self.main_obj['bg_image'],
            size=(int(constants['size_image'][0] * self.system.screen.get_width()),
                  int(constants['size_image'][1] * self.system.screen.get_height())))
        self.rect = [name, artist, rect]
        self.system.objects += self.rect
        self.arrow.rect_surface = pygame.transform.flip(self.arrow.rect_surface, False, True)

    def lock(self):
        """when list is opened and became into close"""
        self.opened = False
        self.drawing_objects = [self.main, self.arrow]
        for obj in self.rect:
            self.system.objects.remove(obj)
        self.arrow.rect_surface = pygame.transform.flip(self.arrow.rect_surface, False, True)

    def get_surface(self):
        """draw objects:"""
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        for obj in self.drawing_objects:
            surface.blit(obj.get_surface(), obj.position)
        return surface

    def click(self, event):
        """
        react to events
        :param event - event pygame"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if abs(event.pos[0] - self.position[0] - self.arrow.position[0] - self.arrow.size[0] / 2) <= \
                    self.arrow.size[1] / 2 and \
                    abs(event.pos[1] - self.position[1] - self.arrow.position[1] - self.arrow.size[1] / 2) <= \
                    self.arrow.size[1] / 2:
                # events with clicking arrow:
                if not self.opened:
                    self.arrow.func[0]()
                    self.opened = True
                else:
                    self.arrow.func[1]()
                    self.opened = False
            else:
                # events with clicking into blocks:
                if self.opened:
                    for obj in self.additional_objects:
                        if abs(event.pos[0] - self.position[0] - obj.position[0] - obj.size[0] / 2) <= obj.size[
                            0] / 2 and abs(event.pos[1] - self.position[1] - obj.position[1] - obj.size[1] / 2) <= \
                                obj.size[1] / 2:
                            obje = self.add_obj_func[obj]
                            obje['func'][0](obje['func'][1], obje['func'][2], obje['func'][3], obje['func'][4])
                            return True

        return False


class DropDownList:
    def __init__(self, position, image, font, font_color, objects, constants, system, music):
        """
        :param position: pos of left high corner of main block
        :param image: image of arrow
        :param font: font of text
        :param font_color: colour of text
        :param objects: [[{'text':'', 'type':main/not_main, 'func':func, 'bg_image':bg_image},...],...,]
        :param constants: constants of game like screen or file with data
        :param system: system of game
        :param music: background music
        """
        self.position = position
        self.image = image
        self.font = font
        self.font_color = font_color
        self.objects = objects
        self.constants = constants
        self.drop_down_lists = []
        self.system = system
        self.music = music
        self.screen = self.system.screen
        # count max size of objects:
        max_size = [0, 0]
        # change font if no freedom space:
        for arr in self.objects:
            for obj in arr:
                f = pygame.font.Font(None, self.font)
                text_surface = f.render(obj['text'], True, self.font_color)
                max_size[0] = max(max_size[0], int(text_surface.get_size()[0] * constants['box_size'][0]))
                max_size[1] = max(max_size[1], int(text_surface.get_size()[1] * constants['box_size'][1]))
        # add objects in working form:
        for obj in self.objects:
            drop_down = DropDown((self.position[0], self.position[1] + self.objects.index(obj) * max_size[1]),
                                 self.image, self.font, self.font_color, obj, self.constants, self.system,
                                 (self.position[0] * self.constants['drop_down']['place_image'], self.position[1]),
                                 main_size=max_size)
            self.drop_down_lists.append(drop_down)

        self.size = (self.drop_down_lists[0].size[0], max_size[1] * 9)

    def get_surface(self):
        """
        draw objects
        :return: surface with pictures of objects
        """
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        for obj in self.drop_down_lists:
            surf = obj.get_surface()
            surface.blit(surf, (obj.position[0] - self.position[0], obj.position[1] - self.position[1]))
        return surface

    def click(self, event):
        """
        react to events
        :param event: pygame Event
        :return: None
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            for obj in self.drop_down_lists:
                status = obj.opened
                # play music:
                buzy = pygame.mixer.music.get_busy()
                pygame.mixer.music.pause()
                if not obj.click(event) and buzy:
                    pygame.mixer.music.play()
                # if close some drop down:
                if status and not obj.opened:
                    for elem in self.drop_down_lists[self.drop_down_lists.index(obj) + 1:]:
                        elem.position = (
                            elem.position[0], elem.position[1] - len(obj.additional_objects) * obj.main.size[1])
                    pygame.mixer.music.stop()

                # if open some drop down:
                if not status and obj.opened:
                    # close others opened drop_down lists and move smth if it needed:
                    for elem in self.drop_down_lists:
                        if elem != obj:
                            if elem.opened:
                                elem.lock()
                                elem.opened = False
                                for element in self.drop_down_lists[self.drop_down_lists.index(elem) + 1:]:
                                    element.position = (element.position[0],
                                                        element.position[1] - len(elem.additional_objects) *
                                                        elem.main.size[1])
                    # move drop_downs if smth opened:
                    for elem in self.drop_down_lists[self.drop_down_lists.index(obj) + 1:]:
                        elem.position = (
                            elem.position[0], elem.position[1] + len(obj.additional_objects) * obj.main.size[1])
                    # play music:
                    for elem in self.objects:
                        if elem == obj.objects:
                            pygame.mixer.music.stop()
                            sound = elem[self.drop_down_lists.index(obj)]['music']
                            pygame.mixer.music.load(sound)
                            pygame.mixer.music.play()


class System:
    # class that have all parametries of during menu-pack
    def __init__(self, bg_image, volume=0.5, dim=0.5, blur=0.5, offset=0.5):
        """
        init for class System
        bg_image - image of background screen
        volume - volume of sound
        dim - characteristic of sound
        blur - characteristic of sound
        offset - contacting sound and picture
        """
        with open('game_config.json', 'r') as f:
            sets = json.load(f)
        self.screen = pygame.display.set_mode((sets['width'], sets['height']))
        self.FPS = sets['FPS']
        self.sets = {'volume': volume, 'dim': dim, 'blur': blur, 'offset': offset}
        self.bg_image = bg_image
        self.objects = []
        # open file of pictures:
        full_path = os.path.abspath(os.curdir)
        folder = os.path.join(pathlib.Path(full_path).parents[0], 'assets')
        self.folder = folder
        # open file with game constants:
        with open('constants.json', 'r') as f:
            self.constants = json.load(f)
        # make background surface:
        self.bg_surface = pygame.image.load(os.path.join(self.folder, self.bg_image)).convert_alpha()
        self.screen.blit(self.bg_surface, (0, 0))
        self.bg_surface = pygame.transform.smoothscale(self.bg_surface,
                                                       (self.screen.get_width(), self.screen.get_height()))
        self.bg_sound = os.path.join(self.folder, 'song.mp3')
        self.place = None
        self.finished = False

    def set(self, name, value):
        # set some parametres of game
        self.sets[name] = value

    def menu(self):
        # open menu
        # read constants from file:
        self.place = self.menu
        screen = self.screen
        w = screen.get_width()
        h = screen.get_height()
        folder = self.folder
        const = self.constants['menu']
        box_size = self.constants['box_size']
        font = self.constants['font']
        # make buttons and textboxes:
        menu = TextBox((w * const['menu'][0], h * const['menu'][1]),
                       font,
                       self.constants['colors']['textbox'], 'Menu', 'center',
                       os.path.join(folder, 'box.jpg'), box_size)
        setting = Button(
            (w * const['settings'][0], h * const['settings'][1]), font,
            self.constants['colors']['button'], 'Settings', 'center', os.path.join(folder, 'rect.png'),
            self.settings, box_size)
        start = Button((w * const['start'][0], h * const['start'][1]), font,
                       self.constants['colors']['button'], 'Start', 'center', os.path.join(folder, 'rect.png'),
                       self.start, box_size)
        _exit = Button((w * const['exit'][0], h * const['exit'][1]), font,
                       self.constants['colors']['button'], 'Exit', 'center', os.path.join(folder, 'rect.png'),
                       self.exit_screensaver,
                       box_size)
        self.objects = [menu, setting, start, _exit]

    def settings(self):
        # open settings-menu
        # read contants from file
        screen = self.screen
        w = screen.get_width()
        h = screen.get_height()
        folder = self.folder
        const = self.constants['settings']
        box_size = self.constants['box_size']
        circle_size = self.constants['circle_size']
        color_on = self.constants['colors']['slider_on']
        color_off = self.constants['colors']['slider_off']
        font = self.constants['font']
        # make buttons and textboxes, sliders:
        menu_box = TextBox((w * const['menu_box'][0], h * const['menu_box'][1]), font,
                           self.constants['colors']['textbox'], 'Settings menu', 'center',
                           os.path.join(folder, 'box.jpg'), box_size)
        volume = TextBox((w * const['volume'][0], h * const['volume'][1]), font,
                         self.constants['colors']['textbox'], 'Volume', 'left', os.path.join(folder, 'box.jpg'),
                         box_size)
        bg_dim = TextBox((w * const['bg_dim'][0], h * const['bg_dim'][1]), font,
                         self.constants['colors']['textbox'], 'Dim', 'left', os.path.join(folder, 'box.jpg'), box_size)
        bg_blur = TextBox((w * const['bg_blur'][0], h * const['bg_blur'][1]), font,
                          self.constants['colors']['textbox'], 'Blur', 'left', os.path.join(folder, 'box.jpg'),
                          box_size)
        offset = TextBox((w * const['offset'][0], h * const['offset'][1]), font,
                         self.constants['colors']['textbox'], 'Offset', 'left', os.path.join(folder, 'box.jpg'),
                         box_size)
        volume_slider = Slider((w * const['volume_slider'][0], h * const['volume_slider'][1]),
                               os.path.join(folder, 'circle.png'), color_on, color_off,
                               (w * const['volume_slider_size'][0], h * const['volume_slider_size'][1]), self, 'volume',
                               font, self.constants['colors']['textbox'], self.sets['volume'], circle_size)
        dim_slider = Slider((w * const['dim_slider'][0], h * const['dim_slider'][1]),
                            os.path.join(folder, 'circle.png'), color_on, color_off,
                            (w * const['dim_slider_size'][0], h * const['dim_slider_size'][1]), self, 'dim',
                            font, self.constants['colors']['textbox'], self.sets['dim'], circle_size)
        blur_slider = Slider((w * const['blur_slider'][0], h * const['blur_slider'][1]),
                             os.path.join(folder, 'circle.png'), color_on, color_off,
                             (w * const['blur_slider_size'][0], h * const['blur_slider_size'][1]), self, 'blur',
                             font, self.constants['colors']['textbox'], self.sets['blur'], circle_size)
        offset_slider = Slider((w * const['offset_slider'][0], h * const['offset_slider'][1]),
                               os.path.join(folder, 'circle.png'), color_on, color_off,
                               (w * const['offset_slider_size'][0], h * const['offset_slider_size'][1]), self, 'offset',
                               font, self.constants['colors']['textbox'], self.sets['offset'], circle_size)

        _exit = Button((w * const['exit'][0], h * const['exit'][1]), font,
                       self.constants['colors']['button'], 'Back', 'left', os.path.join(folder, 'rect.png'), self.place,
                       box_size)
        self.objects = [menu_box, volume, bg_dim, bg_blur, offset, volume_slider, dim_slider, blur_slider,
                        offset_slider, _exit]
        self.place = self.settings

    def start(self):
        screen = self.screen
        self.place = self.start
        w = screen.get_width()
        h = screen.get_height()
        folder = self.folder
        const = self.constants['start']
        # take information about tracks into files:
        beatmap_folder = os.path.join(pathlib.Path(self.folder).parents[0], 'Beatmaps')
        beatmaps = get_beatmaps(beatmap_folder)
        objects = []
        # add songs into drop_down format:
        for beat_map in beatmaps:
            song = []
            file = {'text': beat_map['title'], 'music': beat_map['music_path'], 'type': 'main',
                    'bg_image': beat_map['bg_image'], 'preview': beat_map['preview'], 'title': beat_map['title'],
                    'artist': beat_map['artist'], 'rect_image': os.path.join(self.folder, 'rect_image.jpg')}
            song.append(file)
            for dif in beat_map['diffs']:
                file = {'music': beat_map['music_path'], 'type': 'not_main', 'bg_image': beat_map['bg_image'],
                        'preview': beat_map['preview'], 'text': str(list(dif.keys())[0]),
                        'rect_image': os.path.join(self.folder, 'rect_image.jpg')}
                diff = os.path.join(beat_map['beatmap_directory'], dif[str(list(dif.keys())[0])])
                file['func'] = [start_game, self.screen, beat_map['beatmap_directory'], diff, self.sets['volume'] * 100]
                song.append(file)

            objects.append(song)

        _map = DropDownList((w * const['drop_down_list'][0], h * const['drop_down_list'][1]),
                            os.path.join(self.folder, 'arrow.png'), self.constants['font'],
                            'black', objects, self.constants, self, os.path.join(self.folder, 'arrow.png'))
        # add button:
        setting = Button(
            (w * const['settings'][0], h * const['settings'][1]), self.constants['font'],
            self.constants['colors']['button'], '', 'center', os.path.join(folder, 'settings.png'),
            self.settings,
            self.constants['box_size'],
            (int(w * const['settings_size'][0]), int(h * const['settings_size'][1])))
        self.objects = [_map, setting]

    def play(self):
        # start menu-window
        FPS = self.FPS

        pygame.display.update()
        clock = pygame.time.Clock()
        start_screensaver()
        self.menu()
        while not self.finished:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finished = True
                for obj in system.objects:
                    if type(obj) != TextBox:
                        obj.click(event)

            # play bg music
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(self.bg_sound)
                pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.sets['volume'])

            # draw objects:
            self.screen.blit(self.bg_surface, (0, 0))
            for obj in system.objects:
                self.screen.blit(obj.get_surface(), obj.position)

            pygame.display.update()
        pygame.quit()

    def exit_screensaver(self):
        print('exit')
        self.finished = True


def start_screensaver():
    print('start')


def start_game(screen, beat_map, diff, volume):
    print(beat_map, diff)
    game = GameMaster(screen, beat_map, diff, volume)
    game.start()


# make example of system


system = System('bg.jpg')
system.play()
