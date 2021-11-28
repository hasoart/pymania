# coding:utf-8
import pygame
pygame.font.init()


class TextBox:
    # class textboxes
    def __init__(self, position, bg_image, font, font_color, text, aligment):
        '''
        init for class Textbox
        position - cords of left high corner or center
        bg_image - image in background of text
        font - size of font
        font_color - color of text
        text - text
        aligment - 'center': position - cords of center
                   'left': position - cords of left high corner
        '''
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

    def get_surface(self):
        # get surface of drawing textbox
        # draw background image:
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        rect_surface = pygame.image.load(self.bg_image).convert_alpha()
        rect_surface = pygame.transform.scale(rect_surface, self.size)
        surface.blit(rect_surface, (0, 0))

        # write text
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)
        x_pos = self.size[0] / 2

        text_rect = text_surface.get_rect(center=(x_pos, self.size[1] / 2))
        surface.blit(text_surface, text_rect)

        return surface


class Button(TextBox):
    def __init__(self, position, bg_image, font, font_color, text, aligment, func):
        '''
        init for class Button
        position - cords of left high corner or center
        bg_image - image in background of text
        font - size of font
        font_color - color of text
        text - text
        aligment - 'center': position - cords of center
                   'left': position - cords of left high corner
        func - what to do if button is clicked
        '''
        super().__init__(position, bg_image, font, font_color, text, aligment)
        self.func = func

    def click(self, event):
        '''
        reaction for events:
        do func if clicked
        event - pygame Event
        '''
        if event.type == pygame.MOUSEBUTTONDOWN:
            rho = [event.pos[0] - self.position[0], event.pos[1] - self.position[1]]
            if rho[0] <= self.size[0] and rho[0] >= 0 and rho[1] <= self.size[1] and rho[1] >= 0:
                self.func()


class Slider():
    def __init__(self, position, image, on_color, off_color, size, system, name, value=0.5):
        '''
        init for class Slider (Polzunok)
        position - coords of left high corner
        image - image of circle
        on_color - color of part of rect before circle
        off_color - color of part of rect after circle
        size - size of slider
        value - fraction of part of rect before circle and all rect
        '''
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

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_surface(self):
        # get surface of drawing textbox
        # draw background image:        
        surface = pygame.Surface((self.size[0] * self.circle_scale, self.size[1] * self.circle_scale), pygame.SRCALPHA, 32)
        #draw rects:
        pygame.draw.rect(surface, self.on_color, ((0, self.size[1] * (self.circle_scale - 1) / 2), (self.size[0] * self.value, self.size[1])))
        pygame.draw.rect(surface, self.off_color, ((self.size[0] * self.value, self.size[1] * (self.circle_scale - 1) / 2), (self.size[0] * (1 - self.value), self.size[1])))
        #draw circle:
        circle_surface = pygame.image.load(self.image).convert_alpha()
        circle_surface = pygame.transform.scale(circle_surface, self.circle_size)
        circle_surface.set_colorkey((253, 253, 253))
        surface.blit(circle_surface, (self.size[0] * self.value - self.circle_size[0] / 2, 0))
        return surface

    def click(self, event):
        '''
        reaction for events
        event - pygame Event
        '''
        if event.type == pygame.MOUSEBUTTONDOWN:
            #change status of object if button clicked
            rho = (event.pos[0] - self.circle_pos[0], event.pos[1] - self.circle_pos[1])
            if rho[0] ** 2 + rho[1] ** 2 <= (self.circle_size[1] / 2) ** 2:
                self.condition = True
                
        if event.type == pygame.MOUSEMOTION and self.condition:
            #change position of circle and value 
            if event.pos[0] - self.position[0] <= self.size[0] - self.circle_size[0] / 2 and event.pos[0] - self.position[0] >= self.circle_size[0] / 2:
                self.value = (event.pos[0] - self.position[0] - self.circle_size[0] / 2) / (self.size[0] - self.circle_size[0])
                self.circle_pos = (self.position[0] + self.size[0] * self.value, self.position[1] + self.circle_size[1] / 2)
                system.set(self.name, self.value)
                
        if event.type == pygame.MOUSEBUTTONUP and self.condition:
            #change condition of object if clicked
            self.condition = False


class System():
    #class that have all parametries of during menu-pack or game???
    def __init__(self, bg_image, volume=0.5, dim=0.5, blur=0.5, offset=0.5):
        '''
        init for class System
        bg_image - image of background screen
        volume - volume of sound
        dim - characterist of sound
        blur - characterist of sound
        offset - contacting sound and picture
        '''
        self.volume = volume
        self.dim = dim
        self.blur = blur
        self.offset = offset
        self.screen =''
        self.bg_image=bg_image
        self.objects = []

    def set(self, name, value):
        #set some parametres of game
        if name == 'volume':
            self.volume = value
        if name == 'blur':
            self.blur = value
        if name == 'dim':
            self.dim = value
        if name == 'offset':
            self.offset = value

    def menu(self):
        #open menu
        screen = self.screen
        menu = TextBox((screen.get_width() / 2, screen.get_height() * 2 // 7), 'box.jpg', 50, 'black', 'Menu', 'center')
        setting = Button((screen.get_width() / 2, screen.get_height() * 3 // 7), 'rect.png', 50, 'blue', 'Settings', 'center', self.settings)
        start = Button((screen.get_width() / 2, screen.get_height() * 4 // 7), 'rect.png', 50, 'blue', 'Start', 'center', fun2)
        exit = Button((screen.get_width() / 2, screen.get_height() * 5 // 7), 'rect.png', 50, 'blue', 'Exit', 'center', fun3)
        self.objects = [menu, setting, start, exit]

    def settings(self):
        #open settings-menu
        screen = self.screen
        menu_box = TextBox((screen.get_width() / 2, screen.get_height() * 2 // 8), 'box.jpg', 50, 'black', 'Settings menu', 'center')
        volume = TextBox((screen.get_width() / 6, screen.get_height() * 3 // 8), 'box.jpg', 50, 'black', 'Volume', 'left')
        bg_dim = TextBox((screen.get_width() / 6, screen.get_height() * 4 // 8), 'box.jpg', 50, 'black', 'Dim', 'left')
        bg_blur = TextBox((screen.get_width() / 6, screen.get_height() * 5 // 8), 'box.jpg', 50, 'black', 'Blur', 'left')
        offset = TextBox((screen.get_width() / 6, screen.get_height() * 6 // 8), 'box.jpg', 50, 'black', 'Offset', 'left')
        volume_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 3 // 8), 'circle.png', 'yellow', 'black', (screen.get_width() / 5, screen.get_height() / 60), self, 'volume', self.volume)
        dim_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 4 // 8), 'circle.png', 'green', 'blue', (screen.get_width() / 5, screen.get_height() / 60), self, 'dim', self.dim)
        blur_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 5 // 8), 'circle.png', (108, 225, 64), (142, 0, 0), (screen.get_width() / 5, screen.get_height() / 60), self, 'blur', self.blur)
        offset_slider = Slider((screen.get_width() * 4 // 6, screen.get_height() * 6 // 8), 'circle.png', (228, 228, 61), (96, 49, 74), (screen.get_width() / 5, screen.get_height() / 60), self, 'offset', self.offset)
        exit = Button((screen.get_width() * 4 // 6, screen.get_height() * 7 // 8), 'rect.png', 50, 'blue', 'Back', 'left', self.menu)
        self.objects = [menu_box, volume, bg_dim, bg_blur, offset, volume_slider, dim_slider, blur_slider, offset_slider, exit]
        
    def play(self):
        #start menu-window
        FPS = 30
        self.screen = pygame.display.set_mode((600, 800))
        bg_surface = pygame.image.load(self.bg_image).convert_alpha()
        bg_surface = pygame.transform.scale(bg_surface, (self.screen.get_width(), self.screen.get_height()))
        self.screen.blit(bg_surface, (0, 0))
        pygame.display.update()
        clock = pygame.time.Clock()
        finished = False
        
        system.menu()
        
        while not finished:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True
                for obj in system.objects:
                    if type(obj) != TextBox:
                        obj.click(event)
        
            system.screen.blit(bg_surface, (0, 0))
            for obj in system.objects:
                system.screen.blit(obj.get_surface(), obj.position)
        
            pygame.display.update()        


def fun2(obj):
    #example function
    print('start')
    obj.bg_image = 'pin.jpg'


def fun3(obj):
    #example function
    print('exit')
    obj.bg_image = 'pin.jpg'


# make system
system = System('bg.jpg')
system.play()

pygame.quit()
