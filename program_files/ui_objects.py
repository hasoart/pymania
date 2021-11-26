# coding:utf-8
import pygame
pygame.font.init()


class TextBox:
    def __init__(self, position, bg_image, font, font_color, text, text_aligment, size, shape):
        self.position = position
        self.bg_image = bg_image
        self.font = font
        self.font_color = font_color
        self.text = text
        self.text_aligment = text_aligment
        self.size = size
        self.shape = shape
    
    def get_surface(self):
        #draw textbox
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        rect_surface = pygame.image.load(self.bg_image).convert_alpha()
        rect_surface = pygame.transform.scale(rect_surface,self.size)
        surface.blit(rect_surface, (0,0))
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)
        surface.blit(text_surface, (0,0))          
        return surface

class Button(TextBox):
    def __init__(self, func):
        super().__init__()
        self.func = func
    
    def click(self):
        self.func()
        
        pass


#make background
FPS =20
screen = pygame.display.set_mode((1100, 800))
bg_surface = pygame.image.load('bg.jpg').convert_alpha()
bg_surface = pygame.transform.scale(bg_surface, (screen.get_width(), screen.get_height()))
screen.blit(bg_surface, (0, 0))
pygame.display.update()
clock = pygame.time.Clock()
finished = False


textbox=TextBox((100,300),'rect.png',50,'blue', 'dfdfd',None,(120, 60),None)


while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
    screen.blit(textbox.get_surface(),textbox.position)
    pygame.display.update()

pygame.quit()