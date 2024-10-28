import pygame
import blogger
from renderlib import Screen, Layer

# initialize blogger for global use
blogger.init("log/log")
blog = blogger.blog()

pygame.init()
clock = pygame.time.Clock()
game_screen = pygame.display.set_mode([500,500])

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
                    game_screen.blit(s._render(), (0,0))
            # refresh the screen 1/24 of a second for 24fps
            pygame.display.flip()
            clock.tick(24)
    # register a screen to the screens table
    def addScreen(self, screen: Screen):
        if screen in self.screens:
            return
        else:
            self.screens.append(screen)

class newlayer(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(newlayer, self)._listen("render", self.render)
    def render(self, s):
        pygame.draw.rect(s, (255,255,0), pygame.Rect(30, 30, 60, 60))
        
class newscreen(Screen):
    def __init__(self):
        Screen.__init__(self, pygame.Surface((500,500)))
        super(newscreen, self)._listen("render", self.render)
    def render(self):
        blog.info("hello rendering from 'newscreen'")
        

g = Game()
ns = newscreen()
ns.active = True
nl = newlayer()
nl.active = True
ns.add_layer(nl)
g.addScreen(ns)
g.start()


