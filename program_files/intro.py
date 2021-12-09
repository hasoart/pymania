import pygame as pg
import os


class Video:
    def __init__(self, screen, frequency, path, pos: tuple):
        """
        Initializating object of class Video:
        
            Args:
                screen: window, where the video will be streamed
                frequency: how many screen updates per second will be
                path: path to the folder with all the frames of the video
                pos: position of the bottom right dot of the video
        """
        
        self.screen = screen
        self.frequency = frequency
        self.path = path
        self.position = pos
        
        self.frames = sorted(os.listdir(path))

        self.current_frame = 0
        self.is_playing = False

    def play(self):
        clock = pg.time.Clock()

        while 1:
            self.update()

            clock.tick(FPS)

    def update(self):
        if self.is_playing:
            self.show(self.current_frame)
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
                self.is_playing = False

    def continue(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def show(frame_number):
        frame_name = self.frames[frame_number]
        frame = pg.image.load(self.path + frame_name)
        frame_rect = frame.get_rect(bottomright=pos)

        self.screen.blit(frame, frame_rect)
        pg.display.update()
        
            
            
