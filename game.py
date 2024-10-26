import pygame
import blogger
from screen import Screen

# initialize blogger for global use
blogger.init("log/file")
blog = blogger.blog()

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode([500,500])

# level 1
class Game():
    def __init__(self):
        self.running = True
        self.active_screen = -1
        self.screens = []
        pass
    def start(self):
        # start render loop
        while self.running == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # render the active screen
            for s in self.screens:
                if(s.active == True):
                    s.render()

            # refresh the screen 1/24 of a second for 24fps
            pygame.display.flip()
            clock.tick(24)
    # register a screen to the screens table
    def addScreen(self, screen: Screen):
        if screen in self.screens:
            return
        else:
            self.screens.append(screen)

class newscreen(Screen):
    def __init__(self):
        Screen.__init__(self)
        super(newscreen, self)._listen("render", self.render)
    def render(self):
        print("hello rendering from 'newscreen'")

g = Game()
ns = newscreen()
ns.active = True
g.addScreen(ns)
g.start()


