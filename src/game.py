# dungeon game by Jack Anderson
# 11/20/24
# contains custom class implementations and functions specific to game functionality 
import pygame
import blogger
from renderlib import Screen, Layer, Entity, Collision, EntityFloor
from gamelib import PlayerInfo, LogicComponent, Logic, Tag
from levelslib import Level, parse_efile
import veclib
import random
from veclib import Vec2
# initialize blogger for global use
blogger.init("log/log")
blog = blogger.blog()

pygame.init()
pygame.font.init()
tiny5 = pygame.font.Font('fonts/tiny5.ttf', 30)

clock = pygame.time.Clock()
game_screen = pygame.display.set_mode([512,512])

frame_rate = 24
gameLogic = Logic()
gameLogic.add_component(PlayerInfo("PlayerInfo", 3))

# level 1
class Game():
    def __init__(self):
        self.running = True
        self.screens = []
        
        # Active screen management
        self.active_screen: Screen = None;
    def start(self):
        # start render loop
        while self.running == True:
            screen: Screen
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
            self.active_screen._pre_render()
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
# hotbar at bottom of screen
class Hotbar(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(Hotbar, self)._listen("render", self.render)
        self.dim = Vec2(512,64)
        self.pos = Vec2(0,448)

    def render(self, s:pygame.Surface):
        bd = pygame.Surface(self.dim.arr())
        bd.fill((0,0,0))
        s.blit(bd, self.pos.arr())
        # pull universal player data from the logic class, and use it to update health
        player:PlayerInfo= gameLogic.get_component("PlayerInfo")
        for i in range(0,player.max_health):
            if(player.health - i > 0):
                pygame.draw.rect(self.surface, (255,0,0), pygame.Rect(64+i*32, 448+16,32, 32))
            else:
                pygame.draw.rect(self.surface, (50,0,0), pygame.Rect(64+i*32, 448+16,32, 32))
        
class MainScreen(Screen):
    def __init__(self):
        Screen.__init__(self, pygame.Surface((512,512)))
        # self._listen("event", self.event)

# Entity floor
class Player(Entity):
    def __init__(self):
        Entity.__init__(self)
        self.dim = Vec2(32,32)
        super(Player, self)._listen("event", self.event)
        self.health = 3
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
                    self.floor.add_entity(Projectile((self.relative_position), 16, self.facing.unit(), self))
    def _render(self):
        gpos: Vec2 = self.floor.get_global_position(self.relative_position)
        pygame.draw.rect(self.surface, (255,255,0), pygame.Rect(gpos.x, gpos.y, self.dim.x, self.dim.x))
class Enemy(Entity):
    def __init__(self, ipos:Vec2=Vec2(0,0), colour=(255,0,0), health=3, speed=1):
        Entity.__init__(self)
        self.collidable = True
        self.solid = True
        self.add_tag(Tag.enemy)
        self.relative_position = ipos
        self.dim = Vec2(32,32)
        self.health = health
        self.speed = speed
        self.colour = colour
        
        self.target:Vec2 = Vec2(0,0)
        self.dir:Vec2 = Vec2(0,0)
        # elim any errors by not having initial idea of where player is
        # self.find_player()
        # find the player every 2 seconds, prop to speed
        self._listen_on_interval((2)/self.speed,self.find_player)
        # fire bullets every 2.25 seconds
        self._listen_on_interval((9/4)/self.speed,self.fire_projectile)
        # move based on player location, every 1/2 seconds
        self._listen_on_interval((1/2)/self.speed,self.move)
        

    def fire_projectile(self):
        # cast a ray in the direction of the player, if there's a wall in between don't shoot; can't see through it :)
        entity_in_front = self.floor.raycast(self, self.dir)
        if entity_in_front:
            if Tag.barrier in entity_in_front.tags:
                return
        # offsetdir is a direction with magnitude 1 (unit vector), but has been randomly modified with a slight offset to make the game less impossible :)
        offsetdir:Vec2 = (self.dir + veclib.randvec2(Vec2(0,0), Vec2(1,1))).unit()
        self.floor.add_entity(Projectile(self.relative_position, 12, offsetdir, self))
    def find_player(self):
        # find the player every 2 seconds, and update values for the enemy
        self.target = self.floor.player.relative_position
        self.dir = (self.target - self.relative_position)
    def move(self):
        # TEST IMPLEMENTATION OF PATHFINDING, RANDOMLY MOVE BY COMPONENT
        yx = random.randint(0,1)
        prop_pos: Vec2 = Vec2(0,0)
        if(yx == 0):
            if(self.dir.x > 0):
                prop_pos = self.relative_position + Vec2(self.dim.x,0)
            else:
                prop_pos = self.relative_position + Vec2(-1*self.dim.x,0)
        else:
            if(self.dir.y > 0):
                prop_pos = self.relative_position + Vec2(0,self.dim.y)
            else:
                prop_pos = self.relative_position + Vec2(0,-1*self.dim.y)
        # gets stuck here
        if(self.floor.is_legal_move(self, (prop_pos-self.relative_position))):
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
        # use macro to render (takes colour and gens pos automatically)
        pygame.draw.rect(self.surface, *self.rinfo())
        
class Wall(Entity):
    def __init__(self, ipos:Vec2=Vec2(0,0), colour=(25,25,75)):
        Entity.__init__(self)
        self.collidable = True
        self.colour = colour
        self.solid = True
        self.relative_position = ipos
        # must be gdim of entity floor
        self.dim = Vec2(32,32)
        self.add_tag(Tag.barrier)
    
    def _render(self): 
        gpos = self.floor.get_global_position(self.relative_position)
        pygame.draw.rect(self.surface, self.colour, pygame.Rect(gpos.x,gpos.y, self.dim.x, self.dim.x))

# customizable projectile class for attacks
class Projectile(Entity):
    def __init__(self, ipos = Vec2(0,0), velocity=1, direction=Vec2(1,0), source:Entity=None, damage:int=1):
        Entity.__init__(self)
        self.facing: Vec2 = direction
        self.relative_position: Vec2 = ipos
        self.velocity = velocity
        self.source = source
        self.dim = Vec2(16,16)
        self.collidable = True
        self.solid = False
        self.damage = damage
    def _collision(self, c: Collision):
        # don't damage the entity which shot the projectile
        if(c.entity == self.source):
            return
        # only deal damage to other entities if the bullet came from the player (enemies can't hurt each other)
        if(isinstance(c.entity, Enemy) and isinstance(self.source, Player)):
            # reduce health of entity by the damage of the bullet
            c.entity.health -= self.damage
            self.destroy()
        if(isinstance(c.entity, Player)):
            # access the game logic, and player data, to update health safely
            player: PlayerInfo = gameLogic.get_component("PlayerInfo")
            player.inc_health(-self.damage)
            self.destroy()
        # bullets can't pass through solid objects
        if(c.entity.solid == True):
            self.destroy()
        
    def _render(self):
        # move the bullet by one unit * velocity in the direction self.facing * the ratio of 24fps to the frame rate (velocity of 1 is based on 24fps)
        prop_pos: Vec2 = self.relative_position + ((self.facing * (self.velocity))*(24/frame_rate))
        self.relative_position = prop_pos
        gpos = self.floor.get_global_position(self.relative_position)
        pygame.draw.rect(self.surface, (255,255,0), pygame.Rect(gpos.x, gpos.y, self.dim.x, self.dim.y))

#powerupp test class
class Powerup(Entity):
    def __init__(self, ipos = Vec2(0,0), val=1):
        Entity.__init__(self)
        self.dim = Vec2(16,16)
        self.colour = (10,75,45)
        self.relative_position: Vec2 = ipos
        self.solid = False
        self.val = 1
        self.collidable = True
        self.centred= True
    def _collision(self, c: Collision):
        # give the player more health
        if(isinstance(c.entity, Player)):
            # access the game logic, and player data, to update health safely
            player: PlayerInfo = gameLogic.get_component("PlayerInfo")
            player.inc_health(self.val)
            self.destroy()
    # render in one place.    
    def _render(self):
        # destructure the rinfo macro, gives quick rect and colour info for pygame draw rect
        pygame.draw.rect(self.surface, *self.rinfo())

# entity floor for game; contains entities and functionality
class GameFloor(EntityFloor):
    def __init__(self):
        EntityFloor.__init__(self)
        self.pos: Vec2 = Vec2(64,64)
        self.gdim = 32
        self.player: Entity = None;
        self.dim: Vec2 = Vec2(384,384)
        self._listen("start", self.start)
        self._listen("render", self.render)
        self._listen("event", self.event)
        self.stage = 0
    def event(self, e):
        if e.type == pygame.KEYDOWN:
            # debug keys start with Ctrl
            if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_LCTRL]:
                if e.key == pygame.K_r:
                    self.reset()
                if e.key == pygame.K_t:
                    self.stage+=1
                    self.start(self.stage)
    def render(self):
        stage_text = tiny5.render(str(self.stage), False, (255,255,255))
        self.surface.blit(stage_text, self.get_global_position(Vec2(8,0)).arr())
        if(self.count([Tag.enemy]) == 0):
            self.stage+=1
            self.start(self.stage)
    # initialize a sample level with 4 entities at random grid positions
    def start(self, stage=0):
        if(stage == 0):
            self.load_level(Level(parse_efile("maps/l1.txt"), {'1':Wall, '2':Enemy, '3':Powerup, '4':(lambda: (Enemy(colour=(25,0,0), speed=3, health=2)))}))
        elif(stage == 1):
            self.load_level(Level(parse_efile("maps/l2.txt"), {'1':Wall, '2':Enemy}))
        elif(stage == 2):
            self.load_level(Level(parse_efile("maps/l3.txt"), {'1':Wall, '2':Enemy}))

# initialize game render system (level1,2,3+)
# level 1        
game = Game()
# level 2
mainscreen = MainScreen()
mainscreen.active = True
game.addScreen(mainscreen)
# level 3+
gamefloor = GameFloor()
mainscreen.add_layer(Backdrop())
mainscreen.add_layer(gamefloor)
mainscreen.add_layer(Hotbar())
gamefloor.add_player(Player())

# start the game
game.start()
