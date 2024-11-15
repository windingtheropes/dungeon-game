import pygame
import blogger
import random
from renderlib import Screen, Layer, Entity, Listener, Collision
from vector import Vec2
import math
# initialize blogger for global use
blogger.init("log/log")
blog = blogger.blog()

pygame.init()
clock = pygame.time.Clock()
game_screen = pygame.display.set_mode([512,512])

frame_rate = 60
class Logic(Listener):
    def __init__(self):
        Listener.__init__(self)

# level 1
class Game():
    def __init__(self):
        self.running = True
        self.screens = []
        
        # Active screen management
        self.active_screen: Screen = None;
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
            # allow tick events
            self.active_screen._tick()
            # refresh the screen 1/24 of a second for 24fps
            pygame.display.update()
            clock.tick(frame_rate)
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
        self.dim = Vec2(384,384)
        self.pos = Vec2(64,64)
    def render(self, s:pygame.Surface):
        bd = pygame.Surface(self.dim.arr())
        bd.fill((20,20,40))
        s.blit(bd, self.pos.arr())
class Hotbar(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(Hotbar, self)._listen("render", self.render)
        self.dim = Vec2(512,64)
        self.pos = Vec2(0,448)
        self.T_health = 3 # of 3
    def render(self, s:pygame.Surface):
        bd = pygame.Surface(self.dim.arr())
        bd.fill((0,0,0))
        s.blit(bd, self.pos.arr())
        for i in range(0,3):
            if(self.T_health - i > 0):
                pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(64+i*32, 448+16,32, 32))
            else:
                pygame.draw.rect(self.screen, (50,0,0), pygame.Rect(64+i*32, 448+16,32, 32))
        
class newscreen(Screen):
    def __init__(self):
        Screen.__init__(self, pygame.Surface((512,512)))
    #     super(newscreen, self)._listen_on_interval(2,self.hi)
    #     # super(newscreen, self)._listen("render", self.render)
    # def hi(self):
    #     print("hi")
# Entity floor
class Player(Entity):
    def __init__(self):
        Entity.__init__(self)
        self.dim = Vec2(32,32)
        super(Player, self)._listen("event", self.event)
    
    def event(self, e):
        if(e.type == pygame.KEYDOWN):
            if(e.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]):
                if(e.key == pygame.K_DOWN):
                    self.facing = Vec2(0, self.dim.y)
                elif(e.key == pygame.K_UP):
                    self.facing = Vec2(0, -self.dim.y)
                elif(e.key == pygame.K_RIGHT):
                    self.facing = Vec2(self.dim.x, 0)
                elif(e.key == pygame.K_LEFT):
                    self.facing = Vec2(-self.dim.x, 0)
                # move if legal
                if(self.floor.is_legal_move(self, self.facing)):
                    self.relative_position = self.relative_position + self.facing
            # projectile test
            else:
                if(e.key == pygame.K_e):
                    self.floor.add_entity(Projectile((self.relative_position), 0.75, self.facing, self))
    def _render(self):
        gpos: Vec2 = self.floor.get_global_position(self.relative_position)
        pygame.draw.rect(self.screen, (255,255,0), pygame.Rect(gpos.x, gpos.y, self.dim.x, self.dim.x))
class Enemy(Entity):
    def __init__(self, ipos:Vec2=None):
        Entity.__init__(self)
        self.collidable = True
        self.solid = True
        if(ipos):
            self.relative_position = ipos
        else:
            self.relative_position = Vec2(32,128)
        self.dim = Vec2(32,32)
        self.health = 10
        
        self._listen_on_interval(2,self.find_player)
        self._listen_on_interval(1/2,self.move)
        self.target:Vec2 = Vec2(0,0)
    def find_player(self):
        # find the player every 2 seconds
        self.target = self.floor.player.relative_position
    def move(self):
        # TEST IMPLEMENTATION OF PATHFINDING, RANDOMLY MOVE BY COMPONENT
        dir = (self.target - self.relative_position)
        
        yx = random.randint(0,1)
        prop_pos: Vec2 = Vec2(0,0)
        if(yx == 0):
            if(dir.x > 0):
                prop_pos = self.relative_position + Vec2(self.dim.x,0)
            else:
                prop_pos = self.relative_position + Vec2(-1*self.dim.x,0)
        else:
            if(dir.y > 0):
                prop_pos = self.relative_position + Vec2(0,self.dim.y)
            else:
                prop_pos = self.relative_position + Vec2(0,-1*self.dim.y)
        # gets stuck here
        # if(self.floor.is_legal_move(self, prop_pos)):
        self.relative_position = prop_pos
    def _render(self): 
        self.floor: EntityFloor
        diff = self.relative_position + (-1*(self.floor.player.relative_position))
        # dir = -1*(diff.unit())
        # self.facing = -1 * self.floor.player.facing
        # self.floor.add_entity(Projectile(self.relative_position, 1, dir, self))
        if(self.health <= 0):
            self.destroy()
        # if(self.floor.is_legal_move(self, self.facing)):
        #     self.relative_position = self.relative_position + self.facing
        gpos: Vec2 = self.floor.get_global_position(self.relative_position)
        pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(gpos.x, gpos.y, self.dim.x, self.dim.x))
class Projectile(Entity):
    def __init__(self, ipos = Vec2(0,0), velocity=1, direction=Vec2(1,0), source:Entity=None):
        Entity.__init__(self)
        self.facing: Vec2 = direction
        self.relative_position: Vec2 = ipos
        self.velocity = velocity
        self.source = source
        self.dim = Vec2(16,16)
        self.collidable = True
        self.solid = False
    def _collision(self, c: Collision):
        if(c.entity == self.source):
            return
        
        if(isinstance(c.entity, type(self))):
            return
        if(isinstance(c.entity, Enemy)):
            c.entity.health -= 5
        self.destroy()
    def _render(self):
        # move by one unit of velocity* direction every render cycle, velocity 1 is relative to 24 fps, so multiply by a ratio of this to the frame rate
        prop_pos: Vec2 = self.relative_position + ((self.facing * (self.velocity))*(24/frame_rate))
        self.relative_position = prop_pos
        gpos = self.floor.get_global_position(self.relative_position)
        pygame.draw.rect(self.screen, (255,255,0), pygame.Rect(gpos.x, gpos.y, self.dim.x, self.dim.y))
# the entity floor contains a list of entities, [[Entity, GlobalPosition]]
class EntityFloor(Layer):
    def __init__(self):
        Layer.__init__(self)
        self.entities = []
        self.pos: Vec2 = Vec2(64,64)
        self.gdim = 32
        self.player: Entity = None;
        self.dim: Vec2 = Vec2(384,384)
        # self.listeners = {"render": None, "event": None}
    # layer does not have built in functionality for handling layers within (layer 3.1), so it must be added like it is implemented in screens (layer 2)
    def _render(self):
        if(self.listeners["render"] == None):
        # if no registered listener is present, default behaviour is to render all active layers
            e: Entity
            for e in self.entities:
                rel_pos: Vec2 = e.relative_position
                if(abs(rel_pos.x) > (self.dim.x) or abs(rel_pos.y) > (self.dim.y)) or e._del == True:
                    # remove entities far away from the dimensions of the floor, or when they're queued to be deleted
                    self.entities.remove(e)
                else:
                    # print(e.dim.arr())
                    collision = self.calc_collision(e)
                    if(collision):
                        e._collision(collision)
                    e._render()
                    # ensure that interval functions can run at this level 
                    e._tick()
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
    def add_player(self, player: Entity):
        self.player = player
        self.add_entity(player)
    def add_entity(self, entity: Entity):
        # if entity.dim.x != self.gdim or entity.dim.y != self.gdim:
        #     blog.warn("Mismatch in entity widths from grid dimensions.")
        if entity in self.entities:
           return blog.warn(f"{self.__class__.__name__}) Entity already registered.")
        else:
            # registers the layer to the screen by providing it with a surface to render to
            if(self.screen == None):
                blog.error(f"{self.__class__.__name__}) No screen registered; trying to assign None screen to entity.")
            entity.screen = self.screen
            # give entity access to entityfloor
            entity.floor = self
            self.entities.append(entity)       
    # get the position relative to the screen, useful for rendering of entities 
    def get_global_position(self, relative_position: Vec2):
        return relative_position + self.pos
    def get_grid_position(self, relative_position:Vec2):
        # return position relative to the grid, knowing that all entities are the same size. 
        return(relative_position*(1/self.gdim)).arr()
    # calculate collisions
    def calc_collision(self, entity: Entity, o_pos: Vec2=None):
        target: Entity
        if entity.collidable == False:
            return None
        for target in self.entities:
            if target.collidable == False:
                continue
            # can't collide with self
            if(target == entity):
                continue
            # override position with position if given
            pos: Vec2
            if(o_pos):
                pos = o_pos
            else:
                pos = entity.relative_position
            # print(target.dim.arr())
            # print(entity.dim.arr())
            # hitbox dimension calculations
            t_pos = target.relative_position.abs()
            t_min = Vec2(t_pos.x, t_pos.y)
            t_max = Vec2(t_pos.x+target.dim.x-1, t_pos.y+target.dim.y-1)

            # if(isinstance(entity, Projectile) and not isinstance(target, Projectile)):
            #     blog.info(f"[{target.id}] {target.__class__.__name__}, {t_pos.arr()}")
            #     blog.info(f"[{entity.id}] {entity.__class__.__name__}, {pos.arr()}")
            #     if(pos.abs().x >= t_min.x) and (pos.abs().x <= t_max.x):
            #         print("collision on x")
            #     if(pos.abs().y >= t_min.y) and (pos.abs().y <= t_max.y):
            #         print("collision on y")
            # print(t_min.arr())
            if(
                # entity position is greater than or equal to the minimum x; to the right
                # entity position is less than or equal to the maximum x
                ((pos.x >= t_min.x) and (pos.x <= t_max.x))
                
                and 
                # entity position is greater than or equal to the minimum y; down is positive (thanks pygame :) )
                # entity position is less than or equal to the maximum y
                ((pos.y >= t_min.y) and (pos.y <= t_max.y))
              ):
                # if(isinstance(entity, Projectile) and isinstance(target, Enemy)):
                #     print("collision")
                return Collision(target, pos)
            else:
               # proceed to check next entity in array
               continue
        return None
    # check if a move is legal for any solid entity
    def is_legal_move(self, entity: Entity, dir: Vec2):
        # position is in the top left of every entity, so subtract 1 from the amount of times h or w of entity goes into h or w of floor
        max_x = (((self.dim.x)-entity.dim.x)/entity.dim.x)*entity.dim.x
        max_y = (((self.dim.y)-entity.dim.y)/entity.dim.y)*entity.dim.y
        prop_pos = entity.relative_position + dir
        
        # if a collision is expected on this next move, with a solid entity, treat it as such **** TODO ** and don't allow the move
        collision: Entity = self.calc_collision(entity, prop_pos)
        if(collision and collision.entity.solid == True):
            return False
        # two movements can't be made at the same time currently, but worth checking for the future
        if(dir.x != 0) and (prop_pos.x < 0 or prop_pos.x > max_x):
            return False
        if(dir.y != 0) and (prop_pos.y < 0 or prop_pos.y > max_y):
            return False
        return True

        
        
g = Game()

ns = newscreen()
ns.active = True
g.addScreen(ns)

bd = Backdrop()
hb = Hotbar()
p = Player()
enemy = Enemy()
# enemy2 = Enemy()
# enemy2.relative_position = Vec2(128,128)
ef = EntityFloor()
# proj = Projectile([0,0], 10, Vec2(1,0))
ns.add_layer(bd)
ns.add_layer(ef)
ns.add_layer(hb)
ef.add_player(p)
ef.add_entity(Enemy(Vec2(32,32)))
ef.add_entity(Enemy(Vec2(64,64)))
ef.add_entity(Enemy(Vec2(32,64)))
ef.add_entity(Enemy(Vec2(64,32)))

# ef.add_entity(enemy2)
# ef.add_entity(proj)

g.start()
