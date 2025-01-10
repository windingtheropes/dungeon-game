# dungeon game by Jack Anderson
# 11/20/24
# contains custom class implementations and functions specific to game functionality 
import urllib.request
import pygame
import blogger
import math
from renderlib import Screen, Layer, Entity, Collision, EntityFloor
from gamelib import PlayerInfo, Number, Logic, Tag
from levelslib import Level, parse_efile, parse_emap
from levelgen import gen
import veclib
import random
import clocklib
from sys import exit
from veclib import Vec2
# initialize blogger for global use
blogger.init("log/log")
blog = blogger.blog()
import urllib

# download font
urllib.request.urlretrieve("https://fonts.gstatic.com/s/tiny5/v3/KFOpCnmCvdGT7hw-z0hHAi88.ttf", ".font_dg")
pygame.init()
pygame.font.init()
tiny5 = pygame.font.Font('./.font_dg', 30)
tiny5_20 = pygame.font.Font('./.font_dg', 20)

clocklib.clock = clocklib.Clock()
clock = pygame.time.Clock()
game_screen = pygame.display.set_mode([512,512])
pygame.display.set_caption("Dungeon Game")
frame_rate = 24
gDB = Logic()
gDB.set(Number("highscore",0))
def resetGDB():
    global gDB
    gDB.set(PlayerInfo("PlayerInfo", 3))
    gDB.set(Number("playerprot"))
    gDB.set(Number("stage"))
resetGDB()
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
            # don't check for new active screens if the current one is still active
            if self.active_screen != None and self.active_screen.active == True:
                pass
            else:
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
            # refresh the screen 1/24 of a second for 24fps
            pygame.display.update()
            clock.tick(frame_rate)
    # register a screen to the screens table
    def addScreen(self, screen: Screen):
        if screen in self.screens:
            return
        else:
            self.screens.append(screen)
# health bad at bottom of screen
class DataBar(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(DataBar, self)._listen("render", self.render)
        self.dim = Vec2(512,64)
        self.pos = Vec2(0,448)
        self.full_colour = (255,0,0)
        self.prot_colour = (10,60,175)
        self.empty_colour = (50,0,0)
    def render(self, s:pygame.Surface):
        bd = pygame.Surface(self.dim.arr())
        bd.fill((0,0,0))
        s.blit(bd, self.pos.arr())
        # pull universal player data from the logic class, and use it to update health
        player:PlayerInfo= gDB.get("PlayerInfo")
        for i in range(0,player.max_health):
            if(player.health - i > 0):
                if(gDB.get("playerprot").value == 1):
                    pygame.draw.rect(self.surface, self.prot_colour, pygame.Rect(64+i*32, 448+16,32, 32))
                else:
                    pygame.draw.rect(self.surface, self.full_colour, pygame.Rect(64+i*32, 448+16,32, 32))
            else:
                pygame.draw.rect(self.surface, self.empty_colour, pygame.Rect(64+i*32, 448+16,32, 32))

class GameOverText(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(GameOverText, self)._listen("render", self.render)
        self.dim = Vec2(512,512)
    def render(self, s:pygame.Surface):
        gameover_text = tiny5.render(f"GAME OVER | SCORE {str(gDB.get('stage').value)}", False, (255,255,255))
        highscore_text = tiny5.render(f"HIGH SCORE { str( gDB.get('highscore').value ) }", False, (255,255,255))
        gor = gameover_text.get_rect()
        hsor = gameover_text.get_rect()

        self.surface.blit(gameover_text, Vec2(256-(gor.width/2), 256-(gor.height/2)).arr())
        self.surface.blit(highscore_text, Vec2(256-(hsor.width/2), 256-(hsor.height/2)+gor.height).arr())
       
class PausedOverlay(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(PausedOverlay, self)._listen("render", self.render)
        self._listen("event", self.event)
        self.active = False
        self.selected = 0
        self.exit_code = -1
        self.selected_colour =  (255,50,50)
        self.unselected_colour = (255,255,250)
        self.dim = Vec2(512,512)
    def event(self, e):
        if(self.active == False):
            return
        if(e.type == pygame.KEYDOWN):
            if e.key in [pygame.K_DOWN, pygame.K_UP]:
                self.change_selected()
            if e.key == pygame.K_RETURN:
                self.exit_code = self.selected
                self.active = False
    def change_selected(self):
        if(self.selected == 1):
            self.selected = 0
        else:
            self.selected = 1
    # return appropriate colour (selected or unselected) based on the identifier, id, and self.selected colour
    def sel_col(self, id):
        if self.selected == id:
            return self.selected_colour
        return self.unselected_colour
    def render(self, s:pygame.Surface):
        if(self.active == False):
            return
        title_text = tiny5.render("PAUSED", False, (255,255,250))
        main_menu_text = tiny5.render("MAIN MENU", False, self.sel_col(0))
        exit_text = tiny5.render("QUIT", False, self.sel_col(1))

        ptr = title_text.get_rect()
        uptr = title_text.get_rect()
        etr = title_text.get_rect()

        self.surface.blit(title_text, Vec2(256-(ptr.width/2), 256-(ptr.height/2)-uptr.height).arr())
        self.surface.blit(main_menu_text, Vec2(256-(uptr.width/2), 256-(uptr.height/2)+ptr.height+5).arr())
        self.surface.blit(exit_text, Vec2(256-(etr.width/2), 256-(etr.height/2)+ptr.height+uptr.height+5).arr())
            

class MainMenu(Layer):
    def __init__(self):
        Layer.__init__(self)
        super(MainMenu, self)._listen("render", self.render)
        self._listen("event", self.event)
        self.selected = 0
        self.selected_colour =  (50,255,50)
        self.unselected_colour = (255,255,250)
        self.dim = Vec2(512,512)
        self.exit_code = -1
    def change_selected(self):
        if(self.selected == 1):
            self.selected = 0
        else:
            self.selected = 1
    def event(self, e):
        if(self.active == False):
            return
        if(e.type == pygame.KEYDOWN):
            if e.key in [pygame.K_DOWN, pygame.K_UP]:
                self.change_selected()
            if e.key == pygame.K_RETURN:
                self.exit_code = self.selected
                self.active = False
    # return appropriate colour (selected or unselected) based on the identifier, id, and self.selected colour
    def sel_col(self, id):
        if self.selected == id:
            return self.selected_colour
        return self.unselected_colour
    def render(self, s:pygame.Surface):
        if(self.active == False):
            return
        
        title_text = tiny5.render("dungeon game by jack anderson", False, (255,255,250))
        inst_text = tiny5_20.render("Move with arrow keys | E to shoot | Esc to pause", False, (255,255,250))
        play_text = tiny5.render("PLAY", False, self.sel_col(0))
        exit_text = tiny5.render("EXIT", False, self.sel_col(1))

        ptr = title_text.get_rect()
        itr = inst_text.get_rect()
        uptr = title_text.get_rect()
        etr = title_text.get_rect()

        # stack titles ontop of each other with some padding (5 pixels)
        self.surface.blit(title_text, Vec2(256-(ptr.width/2), 256-(ptr.height/2)-uptr.height).arr())
        self.surface.blit(inst_text, Vec2(256-(ptr.width/2), 256-(ptr.height/2)+uptr.height+5).arr())
        self.surface.blit(play_text, Vec2(256-(uptr.width/2), 256-(uptr.height/2)+itr.height+ptr.height+5).arr())
        self.surface.blit(exit_text, Vec2(256-(etr.width/2), 256-(etr.height/2)+itr.height+ptr.height+uptr.height+5).arr())
            
class MainScreen(Screen):
    def __init__(self):
        Screen.__init__(self, pygame.Surface((512,512)))
        self._listen("event", self.event)
        self._listen("start", self.start)
        self._listen("tick", self.tick)
        self.pause_overlay_index = -1
        self.main_menu_index = -1
        self.gamefloor_index = -1
    def start_game(self):
        resetGDB()
        gamefloor = GameFloor()
        self.gamefloor_index = self.add_layer(gamefloor)
        self.add_layer(DataBar())
        gamefloor.add_player(Player())
    def start(self):
        # initialize perpetual layers (outside of game)
        self.main_menu_index = self.add_layer(MainMenu())
        self.layers[self.main_menu_index].active = True
        self.pause_overlay_index = self.add_layer(PausedOverlay())

    def tick(self):
        if(self.gamefloor_index != -1):
            gamefloor = self.layers[self.gamefloor_index]
            if(gamefloor.gameover == True):
                if(gDB.get("stage").value > gDB.get("highscore").value):
                    gDB.set(Number("highscore", gDB.get("stage").value))
                self.add_layer(GameOverText())
                self._listen_on_interval(2500, self.reset, 1)
            # if game is paused, check if the paused_overlay already handled it before turning on the paused overlay
            # prevents an infinite loop and allows exchange of info
            elif(gamefloor.paused == True):
                pause_overlay = self.layers[self.pause_overlay_index]
                if(pause_overlay.active == False and pause_overlay.exit_code != -1):
                    if pause_overlay.exit_code == 0:
                        pause_overlay.active = False
                        self.reset()
                    elif pause_overlay.exit_code == 1:
                        exit()
                else:
                    self.layers[self.pause_overlay_index].active = True

        main_menu = self.layers[self.main_menu_index]
        # handle the main menu if it returned
        # reset its exit code so that this doesn't trigger again
        if(main_menu.active == False):
            if(main_menu.exit_code == 0):
                self.start_game()
            elif(main_menu.exit_code == 1):
                exit()  
            main_menu.exit_code = -1  
    def reset(self):
        self.layers.clear()
        self.gamefloor_index = -1
        self.start()
    def event(self, e):
        if(e.type == pygame.KEYDOWN):
            if e.key == pygame.K_ESCAPE:
                if(self.gamefloor_index != -1):
                    self.layers[self.gamefloor_index].pause_unpause()

# Entity floor
class Player(Entity):
    def __init__(self):
        Entity.__init__(self)
        self.dim = Vec2(32,32)
        super(Player, self)._listen("event", self.event)
        self.health = 3
        self.move_cooldown = -clocklib.clock.ticks()
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
                # move if legal, and allowed by cooldown
                if(self.floor.is_legal_move(self, self.facing)) and clocklib.clock.ticks() > self.move_cooldown:
                    self.move_cooldown = clocklib.clock.ticks()+50
                    self.relative_position = self.relative_position + self.facing
            # projectile test
            else:
                if(e.key == pygame.K_e):
                    self.floor.add_entity(Projectile((self.relative_position), 16, self.facing.unit(), self))
    def _render(self):
        gpos: Vec2 = self.floor.get_global_position(self.relative_position)
        colour = (255,255,0)
        pygame.draw.rect(self.surface, colour, pygame.Rect(gpos.x, gpos.y, self.dim.x, self.dim.x))
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
        # seed ensures that the movement isn't all in sync
        self.seed = random.randint(0,250) # ms
        self._listen_on_interval((1000+self.seed)/self.speed,self.find_player)
        # fire bullets every 2.25 seconds
        self._listen_on_interval((2250+self.seed)/self.speed,self.fire_projectile)
        # move based on player location, every 1/2 seconds
        self._listen_on_interval((500+self.seed)/self.speed,self.move)
        
    # def s
    def fire_projectile(self):
        # cast a ray in the direction of the player, if there's a wall in between don't shoot; can't see through it :)
        # causes terrible performance
        # entity_in_front = self.floor.raycast(self, self.dir)
        # if entity_in_front:
        #     if Tag.barrier in entity_in_front.tags:
        #         return
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
        # don't damage the entity which shot the projectile, or same type (enemies can't shoot each other)
        if(c.entity == self.source) or (type(c.entity) == type(self.source)):
            return
        # print(type(c.entity) == type(self.source))
        # only deal damage to other entities if the bullet came from the player (enemies can't hurt each other)
        if(isinstance(c.entity, Enemy) and isinstance(self.source, Player)):
            # reduce health of entity by the damage of the bullet
            c.entity.health -= self.damage
            self.destroy()
        if(isinstance(c.entity, Player)):
            # access the game logic, and player data, to update health safely
            player: PlayerInfo = gDB.get("PlayerInfo")
            if(gDB.get("playerprot").value == 0):
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
            player: PlayerInfo = gDB.get("PlayerInfo")
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
        self._listen("tick", self.tick)
        # self.clock = clocklib.clock.ticks
    def event(self, e):
        if e.type == pygame.KEYDOWN:
            # debug keys start with Ctrl
            if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_LCTRL]:
                if e.key == pygame.K_r:
                    self.start()
    def render(self):
        stage_text = tiny5.render(str(gDB.get("stage").value), False, (255,255,255))
        self.surface.blit(stage_text, self.get_global_position(Vec2(8,0)).arr())
    def tick(self):
        if(gDB.get("PlayerInfo").health <= 0):
            self.paused=True
            self.gameover=True
        if(self.count([Tag.enemy]) == 0):
            stage: Number = gDB.get("stage")
            stage.inc()
            self.start()
    # initialize a sample level with 4 entities at random grid positions
    def start(self):
        def reset_prot():
            gDB.get("playerprot").value = 0
        gDB.get("playerprot").value = 1
        self._listen_on_interval(1750, reset_prot,1)
        stage: Number = gDB.get("stage")
        # scale speed of enemies logarithmically
        speed = lambda x: 1.123*math.log10(3*(x+1)) + 0.16
        self.load_level(Level(parse_emap(gen()), {'1':Wall, '2':(lambda: (Enemy(colour=(255,0,0), speed=speed(stage.value), health=2))), '3':Powerup, '4':(lambda: (Enemy(colour=(25,0,0), speed=3, health=2)))}))

# initialize game render system (level1,2,3+)
# level 1        
game = Game()
# level 2
mainscreen = MainScreen()
mainscreen.active = True
game.addScreen(mainscreen)
# level 3+


# start the game
game.start()
