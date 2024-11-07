import pygame
import blogger
from renderlib import Screen, Layer, Entity

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
        self.screens = []
        
        # Active screen management
        self.active_screen = None;
    def start(self):
        active_screen = None
        # start render loop
        while self.running == True:
            for screen in self.screens:
                if(screen.active == True):
                    if(self.active_screen != None and screen.id == self.active_screen.id):
                        pass
                    else:
                        self.active_screen = screen
                        screen._start()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                screen._event(event)
            # render the active screen, by rendering its surface to the main screen
            game_screen.blit(self.active_screen._render(), (0,0))
            # refresh the screen 1/24 of a second for 24fps
            pygame.display.flip()
            clock.tick(24)
    # register a screen to the screens table
    def addScreen(self, screen: Screen):
        if screen in self.screens:
            return
        else:
            self.screens.append(screen)

class Backdrop(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(Backdrop, self)._listen("render", self.render)
    def render(self, s):
        s.fill((255,255,255))
        pass
class newscreen(Screen):
    def __init__(self):
        Screen.__init__(self, pygame.Surface((500,500)))
        # super(newscreen, self)._listen("render", self.render)
# Entity floor
class Player(Entity):
    def __init__(self):
        Entity.__init__(self)
        super(Player, self)._listen("event", self.event)
    def event(self, e):
        if(e.type == pygame.KEYDOWN):
            if(e.key == pygame.K_DOWN):
                self.position[1] += 5
            if(e.key == pygame.K_UP):
                self.position[1] -= 5
            if(e.key == pygame.K_RIGHT):
                self.position[0] += 5
            if(e.key == pygame.K_LEFT):
                self.position[0] -= 5
    def _render(self):
        pygame.draw.rect(self.screen, (255,255,0), pygame.Rect(self._position[0], self._position[1], 60,60))
# the entity floor contains a list of entities, [[Entity, GlobalPosition]]
class EntityFloor(Layer):
    def __init__(self):
        Layer.__init__(self)
        self.entities = []
        self.pos = [50,50]
        self.dim = [300,300]
    
    # layer does not have built in functionality for handling layers within (layer 3.1), so it must be added like it is implemented in screens (layer 2)
    def _render(self):
        if(self.listeners["render"] == None):
        # if no registered listener is present, default behaviour is to render all active layers
            for e in self.entities:
                if e.active == True:
                    # calculated global position
                    cgp = [e.position[0]+self.pos[0], e.position[1]+self.pos[1]]
                    e._position = cgp 
                    print(e.position)
                    e._render()
        else:
            self.listeners["render"]()
    def _event(self, event):
        if(self.listeners["event"] == None):
            # default behaviour if no event function is registered.
            for entity in self.entities:
                if entity.active==True:
                    entity._event(event)
        else:
            self.listeners["event"](event)
    def add_entity(self, entity: Entity):
        if entity in self.entities:
            blogger.blog().warn(f"{self.__class__.__name__}) Entity already registered.")
        else:
            # registers the layer to the screen by providing it with a surface to render to
            if(self.screen == None):
                blogger.blog().error(f"{self.__class__.__name__}) No screen registered; trying to assign None screen to entity.")
            entity.screen = self.screen
            self.entities.append(entity)        

g = Game()

ns = newscreen()
ns.active = True
g.addScreen(ns)

bd = Backdrop()

p = Player()
ef = EntityFloor()
ns.add_layer(bd)
ns.add_layer(ef)
ef.add_entity(p)

g.start()


