import pygame as pg
import os


class Video:
    """
    Class that allows to show a couple of frames in the game window
    """
    def __init__(self, screen, frequency, path, pos: tuple):
        """
        Initializating object of class Video
        
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
        
        self.frames = sorted(os.listdir(path))  # list of frames' names

        self.current_frame = 0  # number in a list of current playing frame
        self.is_playing = False

    def play(self):
        """
        Launches the whole video without possibility to stop
        (in future here may be checked events to have an ability to stop video)
        """
        self.ccontinue()
        clock = pg.time.Clock()

        while self.is_playing:
            self.update()

            clock.tick(self.frequency)

    def update(self):
        """
        Updating frame
        """
        self.show(self.current_frame)
        self.current_frame += 1
            
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
            self.pause()
                
    def ccontinue(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def show(self, frame_number):
        """
        Showing the frame on the screen

            Args:
                frame_number: number of the frame in the list self.frames
        """
        frame_name = self.frames[frame_number]
        frame = pg.image.load(self.path + frame_name)
        frame_rect = frame.get_rect(bottomright=self.position)

        self.screen.blit(frame, frame_rect)
        pg.display.update()

    def reverse(self):
        """
        Reversing the video, so as the fist frame becomes the last, the second
        becomes pre-last etc.
        """
        self.frames = [self.frames[i] for i in range(len(self.frames) - 1, -1, -1)]
    
