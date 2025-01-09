import pygame

class Clock():
    def __init__(self):
        self.frozen = False
        self.frozen_time = 0
    def freeze(self):
        self.frozen = True
        self.frozen_time = pygame.time.get_ticks()
    def ticks(self):
        if(self.frozen == True):
            return self.frozen_time
        return pygame.time.get_ticks()
clock: Clock = None
