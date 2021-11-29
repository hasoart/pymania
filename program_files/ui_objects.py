# coding:utf-8
import pygame
import os
import pathlib
import json

pygame.font.init()


class TextBox:
    # class textbox
    def __init__(self, position, font, font_color, text, aligment, bg_image=None):
        """
        init for class Textbox
        position - cords of left high corner or center
        bg_image - image in background of text
        font - size of font
        font_color - color of text
        text - text
        aligment - 'center': position - cords of center
                   'left': position - cords of left high corner
        """
        self.position = position
        self.bg_image = bg_image
        self.font = font
        self.font_color = font_color
        self.text = text
        self.aligment = aligment
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)
        # count size based on size of text:
        self.size = (text_surface.get_width() * 6 // 5, text_surface.get_height() * 6 // 5)
        if self.aligment == 'center':
            self.position = [self.position[0] - self.size[0] / 2, self.position[1] - self.size[1] / 2]
        if self.bg_image:
            rect_surface = pygame.image.load(self.bg_image).convert_alpha()
            self.rect_surface = pygame.transform.scale(rect_surface, self.size)

    def get_surface(self):
        # get surface of drawing textbox
        # draw background image:
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        if self.rect_surface:
            surface.blit(self.rect_surface, (0, 0))

        # write text
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)
        x_pos = self.size[0] / 2

        text_rect = text_surface.get_rect(center=(x_pos, self.size[1] / 2))
        surface.blit(text_surface, text_rect)

        return surface


class Button(TextBox):
    def __init__(self, position, font, font_color, text, aligment, bg_image, func):
        """
        init for class Button
        position - cords of left high corner or center
        bg_image - image in background of text
        font - size of font
        font_color - color of text
        text - text
        aligment - 'center': position - cords of center
                   'left': position - cords of left high corner
        func - what to do if button is clicked
        """
        super().__init__(position, font, font_color, text, aligment, bg_image)
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
    def __init__(self, position, image, on_color, off_color, size, system, name, value=0.5):
        """
        init for class Slider (Polzunok)
        position - coords of left high corner
        image - image of circle
        on_color - color of part of rect before circle
        off_color - color of part of rect after circle
        size - size of slider
        value - fraction of part of rect before circle and all rect
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
        self.circle_scale = 1.3
        self.circle_size = (int(self.size[1] * self.circle_scale), int(self.size[1] * self.circle_scale))
        self.circle_pos = (self.position[0] + self.size[0] * self.value, self.position[1] + self.circle_size[1] / 2)
        self.circle_surface = pygame.image.load(self.image).convert_alpha()
        self.circle_surface = pygame.transform.scale(self.circle_surface, self.circle_size)
        self.circle_surface.set_colorkey((253, 253, 253))

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_surface(self):
        # get surface of drawing textbox
        # draw background image:
        surface = pygame.Surface((self.size[0] * self.circle_scale, self.size[1] * self.circle_scale), pygame.SRCALPHA,
                                 32)
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


class System:
    # class that have all parametries of during menu-pack or game???
    def __init__(self, bg_image, screen, volume=0.5, dim=0.5, blur=0.5, offset=0.5):
        """
        init for class System
        bg_image - image of background screen
        volume - volume of sound
        dim - characterist of sound
        blur - characterist of sound
        offset - contacting sound and picture
        """
        self.sets = {'volume': volume, 'dim': dim, 'blur': blur, 'offset': offset}
        self.screen = screen
        self.bg_image = bg_image
        self.objects = []
        full_path = os.path.abspath(os.curdir)
        folder = os.path.join(pathlib.Path(full_path).parents[0], 'assets')
        self.folder = folder
        with open('constants.json', 'r') as f:
            self.constants = json.load(f)
        self.bg_surface = pygame.image.load(os.path.join(self.folder, self.bg_image)).convert_alpha()
        self.screen.blit(self.bg_surface, (0, 0))
        self.bg_surface = pygame.transform.scale(self.bg_surface, (self.screen.get_width(), self.screen.get_height()))

    def set(self, name, value):
        # set some parametres of game
        self.sets[name] = value

    def menu(self):
        # open menu
        screen = self.screen
        folder = self.folder
        const = self.constants['menu']
        menu = TextBox((screen.get_width() * const['menu'][0], screen.get_height() * const['menu'][1]),
                       50,
                       self.constants['colors']['textbox'], 'Menu', 'center', os.path.join(folder, 'box.jpg'))
        setting = Button(
            (screen.get_width() * const['settings'][0], screen.get_height() * const['settings'][1]), 50,
            self.constants['colors']['button'], 'Settings', 'center', os.path.join(folder, 'rect.png'), self.settings)
        start = Button((screen.get_width() * const['start'][0], screen.get_height() * const['start'][1]), 50,
                       self.constants['colors']['button'], 'Start', 'center', os.path.join(folder, 'rect.png'), fun2)
        exit = Button((screen.get_width() * const['exit'][0], screen.get_height() * const['exit'][1]), 50,
                      self.constants['colors']['button'], 'Exit', 'center', os.path.join(folder, 'rect.png'), fun3)
        self.objects = [menu, setting, start, exit]

    def settings(self):
        # open settings-menu
        screen = self.screen
        folder = self.folder
        menu_box = TextBox((screen.get_width() / 2, screen.get_height() * 2 // 8), 50,
                           'black', 'Settings menu', 'center', os.path.join(folder, 'box.jpg'))
        volume = TextBox((screen.get_width() / 6, screen.get_height() * 3 // 8), 50,
                         'black', 'Volume', 'left', os.path.join(folder, 'box.jpg'))
        bg_dim = TextBox((screen.get_width() / 6, screen.get_height() * 4 // 8), 50,
                         'black', 'Dim', 'left', os.path.join(folder, 'box.jpg'))
        bg_blur = TextBox((screen.get_width() / 6, screen.get_height() * 5 // 8), 50,
                          'black', 'Blur', 'left', os.path.join(folder, 'box.jpg'))
        offset = TextBox((screen.get_width() / 6, screen.get_height() * 6 // 8), 50,
                         'black', 'Offset', 'left', os.path.join(folder, 'box.jpg'))
        volume_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 3 // 8),
                               os.path.join(folder, 'circle.png'), 'yellow', 'black',
                               (screen.get_width() / 5, screen.get_height() / 60), self, 'volume', self.sets['volume'])
        dim_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 4 // 8),
                            os.path.join(folder, 'circle.png'), 'green', 'blue',
                            (screen.get_width() / 5, screen.get_height() / 60), self, 'dim', self.sets['dim'])
        blur_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 5 // 8),
                             os.path.join(folder, 'circle.png'), (108, 225, 64), (142, 0, 0),
                             (screen.get_width() / 5, screen.get_height() / 60), self, 'blur', self.sets['blur'])
        offset_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 6 // 8),
                               os.path.join(folder, 'circle.png'), (228, 228, 61), (96, 49, 74),
                               (screen.get_width() / 5, screen.get_height() / 60), self, 'offset', self.sets['offset'])
        exit = Button((screen.get_width() * 4 // 6, screen.get_height() * 7 // 8), 50,
                      'blue', 'Back', 'left', os.path.join(folder, 'rect.png'), self.menu)
        self.objects = [menu_box, volume, bg_dim, bg_blur, offset, volume_slider, dim_slider, blur_slider,
                        offset_slider, exit]

    def play(self):
        # start menu-window
        FPS = 30

        pygame.display.update()
        clock = pygame.time.Clock()
        finished = False

        self.menu()

        while not finished:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True
                for obj in system.objects:
                    if type(obj) != TextBox:
                        obj.click(event)

            self.screen.blit(self.bg_surface, (0, 0))
            for obj in system.objects:
                self.screen.blit(obj.get_surface(), obj.position)

            pygame.display.update()


def fun2(obj):
    # example function
    print('start')
    obj.bg_image = 'pin.jpg'


def fun3(obj):
    # example function
    print('exit')
    obj.bg_image = 'pin.jpg'


# make system

screen = pygame.display.set_mode((900, 600))
system = System('bg.jpg', screen)
system.play()

pygame.quit()

'''
TODO:
constants into file
number near slider

add music

'''
