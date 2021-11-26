# coding:utf-8
import pygame
pygame.font.init()


class TextBox:
    def __init__(self, position, bg_image, font, font_color, text, text_aligment, shape):
        self.position = position
        self.bg_image = bg_image
        self.font = font
        self.font_color = font_color
        self.text = text
        self.text_aligment = text_aligment
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)
        self.size = (text_surface.get_width() * 6 // 5, text_surface.get_height() * 6 // 5)
        self.shape = shape
    
    def get_surface(self):
        #draw textbox
        surface = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        rect_surface = pygame.image.load(self.bg_image).convert_alpha()
        rect_surface = pygame.transform.scale(rect_surface,self.size)
        surface.blit(rect_surface, (0,0))
        
        f = pygame.font.Font(None, self.font)
        text_surface = f.render(self.text, True, self.font_color)
        if self.text_aligment=='center':
            x_pos = self.size[0]/2
        if self.text_aligment=='left':
            x_pos=text_surface.get_width()/2
            
        text_rect = text_surface.get_rect(center=(x_pos, self.size[1]/2))
        surface.blit(text_surface, text_rect)  
        
        return surface

class Button(TextBox):
    def __init__(self, position, bg_image, font, font_color, text, text_aligment, shape, func):
        super().__init__(position, bg_image, font, font_color, text, text_aligment, shape)
        self.func = func
    
    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] - self.position[0] <= self.size[0] and event.pos[1] - self.position[1] <= self.size[1]:
                self.func()
          

#make background
FPS =20
screen = pygame.display.set_mode((1100, 800))
bg_surface = pygame.image.load('bg.jpg').convert_alpha()
bg_surface = pygame.transform.scale(bg_surface, (screen.get_width(), screen.get_height()))
screen.blit(bg_surface, (0, 0))
pygame.display.update()
clock = pygame.time.Clock()
finished = False

#example and check working
def fun1():
    print('button1')
def fun2():
    print('button2')

textbox=TextBox((100,300),'rect.png',50,'blue', 'box','left',None)
button1 = Button((400,300),'rect.png',50,'blue', 'button1','left',None, fun1)
button2 = Button((400,500),'rect.png',50,'blue', 'button2','center',None, fun2)
buttons = [button1, button2]

while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        for button in buttons:
            button.click(event)
    
    screen.blit(textbox.get_surface(),textbox.position)
    for button in buttons:
        screen.blit(button.get_surface(),button.position)    
    pygame.display.update()

pygame.quit()