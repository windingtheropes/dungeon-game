# renderlib by Jack Anderson
# 11/20/24
# implements Level 1,2,3 render structure per https://docs.google.com/document/d/1gRGcpoxPOT0HK_joQM001BRy1xtQ2T49LbS1ujOnfrU
# game engine written for use with pygame
import types
import blogger
import time
import random
import pygame
from veclib import Vec2, Ray
from levelslib import Level
# from util import get_highest_of_arr, get_lowest_of_arr, arr_ascending, arr_descending
from collections import deque

# generic renderer; layer 2 or layer 3; includes listener registration, render and event functions.
class IntervalFunction:
    def __init__(self, fun, interval, rep, now):
        self.fun = fun
        self.interval = interval
        self.last = now
        self.repeats = rep
        self.runs = 0
class Listener(): 
    def __init__(self):
        # listeners must be initialized as None in order to be considered valid
        self.listeners = {"tick":None}
        self.interval_listeners = []
    # register a function to the listeners table
    def _listen(self, eventName, fun): 
        allowed_events = self.listeners.keys()
        if eventName in allowed_events:
            if fun != None and type(fun) in [types.MethodType, types.FunctionType]:
                self.listeners[eventName] = fun
            else:
                blogger.blog.warn(f"{self.__class__.__name__}) Function passed for {eventName} listener is not a function.")
        else:
            blogger.blog.warn(f"{self.__class__.__name__}) Event {eventName} does not exist on {self.__class__.__name__}.")
    # interval in s
    def _listen_on_interval(self, interval, fun, rep=0):
        if not interval:
            return blogger.blog.error(f"{self.__class__.__name__}) No interval passed for interval listeners.")
        if fun != None and type(fun) in [types.MethodType, types.FunctionType]:
            self.interval_listeners.append(IntervalFunction(fun, interval*1000, rep, pygame.time.get_ticks()))
        else:
            blogger.blog.warn(f"{self.__class__.__name__}) Function passed for interval listener is not a function.")
    # reset all interval listeners to now, so they will wait for their specified interval to run. useful for new game stages.
    def reset_interval_listeners(self): 
        for int_fun in self.interval_listeners:
            now = pygame.time.get_ticks()
            int_fun: IntervalFunction
            int_fun.last == now
    def _tick(self):
        for int_fun in self.interval_listeners:
            now = pygame.time.get_ticks()
            int_fun: IntervalFunction
            # if there's a limit on how many times this listener will run, and it's been hit, remove the listener and continue checking for others
            if(int_fun.repeats != 0 and int_fun.runs == int_fun.repeats):
                self.interval_listeners.remove(int_fun)
                continue
            if(now - int_fun.last) >= int_fun.interval:
                int_fun.last = now
                int_fun.fun()
                if(int_fun.repeats != 0):
                    int_fun.runs += 1
        if(self.listeners["tick"] != None):
            self.listeners["tick"]()
class Renderer(Listener):
    def __init__(self):
        Listener.__init__(self)
        self.active = True
        self.id = str(int(time.time() * random.random() * random.random()))
        self.listeners.update({
            "event": None,
            "pre_render": None,
            "render": None,
            "start": None
        })
    # universal generic functions trigger registered listeners. this is the function that is run by the layer 1
    def _event(self, e):
        if(self.listeners["event"] != None):
            self.listeners["event"](e)
    def _render(self):
        if(self.listeners["render"] != None):
            self.listeners["render"]()
    # pre render; meant for working within the game loop, not rendering to screen
    def _pre_render(self):
        if(self.listeners["pre_render"] != None):
            self.listeners["pre_render"]()
    def _start(self):
        if(self.listeners["start"] != None):
            self.listeners["start"]()
        
# level 3 - layer, renders to a screen; renders to the screen's surface.
class Layer(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.paused = False
        self.surface:pygame.Surface = None
    # override layer _start to add the stage parameter for on_game_start 
    def _start(self, stage=0):
        if(self.listeners["start"] != None):
            self.listeners["start"](stage)
    # overriden render function, SAME SIGNATURE; gives a variable for a surface to render to.
    def _render(self):
        if(self.listeners["render"] != None):
            if(self.surface == None):
                blogger.blog().warn(f"{self.__class__.__name__}) Layer not initialized to a screen, not rendering.")
                return
            else:
                self.listeners["render"](self.surface)
# level 2 - layer, rendered to a screen; root _render returns a surface which is rendered to layer 1. all items must be rendered to self.surface.
class Screen(Renderer):
    def __init__(self, surface):
        Renderer.__init__(self)
        self.render_screen = True
        self.layers = deque()
        self.surface:pygame.surface = surface;
    # clear the screen
    def _clear(self):
        self.layers = deque()
    # run start function of all layers within no matter what.
    def _start(self):
        l: Layer
        for l in self.layers:
            l._start()
        if(self.listeners["start"]):
            self.listeners["start"]()
    # adding a layer to a screen involves registering it
    def add_layer(self, layer: Layer):
        if layer in self.layers:
            blogger.blog().warn(f"{self.__class__.__name__}) Layer already registered.")
        else:
            # registers the layer to the screen by providing it with a surface to render to
            layer.surface = self.surface
            self.layers.append(layer)
        # listen
        # super(newscreen, self)._listen("render", self.render)
    # methods overriden from Renderer class, MUST MATCH SIGNATURE
    def _event(self, e):
        # prevent lockout by running screen events above layer events
        if(self.listeners["event"] != None):
            # trigger event if it exists
            self.listeners["event"](e)
        if(self.render_screen == False):
            return
        # send all events to layers
        for l in self.layers:
            if l.active==True:
                l._event(e)
    def _pre_render(self):
        if self.render_screen == False:
            return
        # run pre render on inside layers automatically, allow for flexibility regardless whether prerender used on Screen class
        for l in self.layers:
            if l.active==True:
                l._pre_render()
        if(self.listeners["pre_render"] != None):
            self.listeners["pre_render"]()
    def _render(self):
        if(self.render_screen == False):
            return self.surface
        # ensure that tick events can run on the screen
        self._tick()
        # render the background color as a backup, in order to prevent unexpected behaviour
        # self.surface.fill((0,0,0))
        # if no registered listener is present, default behaviour is to render all active layers
        l: Layer
        for l in self.layers:
            if l.active == True:
                # ensure that interval listeners can run on layers
                l._tick()
                l._render()
        if(self.listeners["render"] != None):
            self.listeners["render"]()
        return self.surface
# entity extends layer, contains some extra functions such as collisions, health, colour, and dynamic rendering based on its parent, the entity floor
class Entity(Layer):
    def __init__(self):
        Layer.__init__(self)
        # tells parent to kill this item
        self._del = False
        # will collisions be calculated for this entity
        self.collidable = True
        # if solid, most items cannot pass through this entity
        self.solid = True
        # append collision to allowed events for entity
        self.listeners.update({"collision": None})
        self.tags = []
        # relative to entity floor
        self.relative_position = Vec2(0,0)
        self.dim = Vec2(32,32)
        self.facing = Vec2(0,0) # direction entity is facing
        # entity floor which this entity belongs to. Will only be given this through registration
        self.floor:EntityFloor = None
        self.centred= False
        self.colour = (255,255,255)
    # tagging functions
    def has_tag(self, tag):
        if tag in self.tags:
            return True
        return False
    def add_tag(self, tag):
        if not tag in self.tags:
            self.tags.append(tag)
        else:
            blogger.blog().warn("Can't add a tag twice.")
    # root collision function, trigger the collision listener on an entity
    def _collision(self, c):
        if(self.listeners["collision"] != None):
            self.listeners["collision"](c)   
    # tell the entity floor that this entity can be deleted
    def destroy(self):
        self._del = True
    # return a destructurable array to pass into pygame.draw.rect, based on the relative position.
    # macro for quicker and more consistent rendering
    def rinfo(self):
        gpos = self.floor.get_global_position(self.relative_position)
        # if centred, will treat the relative position as the centre for rendering
        if(self.centred == True):
            return [self.colour, pygame.Rect(gpos.x+self.dim.x/2, gpos.y+self.dim.y/2, self.dim.x, self.dim.y)]
        else:
            return [self.colour, pygame.Rect(gpos.x, gpos.y, self.dim.x, self.dim.y)]
# entity template, used to make copies of a configured entity        

# entity floor base class; contains active entities
class EntityFloor(Layer):
    def __init__(self):
        Layer.__init__(self)
        self.entities = deque()
        self.pos: Vec2 = Vec2(64,64)
        self.background_colour = (20,20,40)
        # grid dimensions, as a reference unit for certain calculations
        self.gameover = False
        self.gdim = 32
        self.player: Entity = None;
        self.dim: Vec2 = Vec2(384,384)
    def pause_unpause(self):
        self.paused = not self.paused
    # layer does not have built in functionality for handling layers within (layer 3.1), so it must be added like it is implemented in screens (layer 2)
    def _render(self):
        if self.paused == True:
            return
        
        # backdrop
        bd = pygame.Surface(self.dim.arr())
        bd.fill(self.background_colour)
        self.surface.blit(bd, self.pos.arr())

        # render entities and calculate collisions
        e: Entity
        for e in self.entities:
            if e.active == True:
                rel_pos: Vec2 = e.relative_position
                if(abs(rel_pos.x) > (self.dim.x) or abs(rel_pos.y) > (self.dim.y)) or e._del == True:
                    # remove entities far away from the dimensions of the floor, or when they're queued to be deleted
                    self.entities.remove(e)
                else:
                    # full functionality for running game
                    collision = self.calc_collision(e, e.relative_position)
                    if(collision):
                        e._collision(collision)
                    e._render()
                    # ensure that interval functions can run at this level 
                    e._tick()
        # run registered render function after these default actions, if it exists
        if(self.listeners["render"] != None):
            self.listeners["render"]()                
    def _event(self, event):
        # don't pass events when paused
        if(self.paused == True):
            return
        # trigger events on all child entities
        for entity in self.entities:
            if entity.active==True:
                entity._event(event)
        # trigger listener as well, if it exists
        if(self.listeners["event"] != None):
            self.listeners["event"](event)
    # must override start function to trigger start on entities, as Layer does not have implementation for layers within
    def _start(self, stage=0):
        # run regardless of if there's a listener or not, to ensure always triggered
        for entity in self.entities:
            if entity.active==True:
                entity._start(stage)
        if(not self.listeners["start"] == None):
            self.listeners["start"](stage)
    def _pre_render(self):
        # run regardless of if there's a listener or not, to ensure always triggered
        for entity in self.entities:
            if entity.active==True:
                entity._pre_render()
        if(not self.listeners["pre_render"] == None):
            self.listeners["pre_render"]()
    def add_player(self, player: Entity):
        self.player = player
        self.add_entity(player)
    def add_entity(self, entity: Entity, force:bool=False):
        # if entity.dim.x != self.gdim or entity.dim.y != self.gdim:
        #     blog.warn("Mismatch in entity widths from grid dimensions.")
        if entity in self.entities:
           return blogger.blog().warn(f"{self.__class__.__name__}) Entity already registered.")
        else:
            # registers the layer to the screen by providing it with a surface to render to
            if(self.surface == None):
                blogger.blog().error(f"{self.__class__.__name__}) No screen registered; trying to assign None screen to entity.")
            entity.surface = self.surface
            # give entity access to entityfloor
            entity.floor = self
            self.entities.append(entity)       
    # get the position relative to the screen, useful for rendering of entities 
    def get_global_position(self, relative_position: Vec2):
        return relative_position + self.pos
    # *convert a relative position to grid coordinates, based on self.gdim (height of a grid square)
    def get_grid_position(self, relative_position:Vec2):
        # return position relative to the grid, knowing that all entities are the same size. 
        return(relative_position*(1/self.gdim))
    # convert grid position [1,0] to relative position, [1*self.gdim,0]
    def get_pos_from_grid(self, grid_position:Vec2):
        return (grid_position * self.gdim)        
    # calculate a collision for an entity
    def calc_collision(self, entity: Entity, relative_position: Vec2=None):
        ### TODO CHECK FOR FOR DIRECT NEXT-TO COLLISIONS INSTEAD OF INSIDE COLLISIONS
        target: Entity
        if entity.collidable == False:
            return None
        e_at_pos: Entity = self.entity_at_point(relative_position)
        if(e_at_pos):
            return Collision(e_at_pos, relative_position)

        else:
            return None
    # is entity at point
    def entity_at_point(self, point: Vec2=None):
        entity: Entity
        for entity in self.entities:
            # hitbox dimension calculations
            t_pos = entity.relative_position.abs()
            t_min = Vec2(t_pos.x, t_pos.y)
            t_max = Vec2(t_pos.x+entity.dim.x-1, t_pos.y+entity.dim.y-1)
            
            if(
                # entity position is greater than or equal to the minimum x; to the right
                # entity position is less than or equal to the maximum x
                ((point.x >= t_min.x) and (point.x <= t_max.x))
                
                and 
                # entity position is greater than or equal to the minimum y; down is positive (thanks pygame :) )
                # entity position is less than or equal to the maximum y
                ((point.y >= t_min.y) and (point.y <= t_max.y))
              ):
                return entity
            else:
               # proceed to check next entity in array
               continue
        return None
    # check if a move is legal for any solid entity
    def is_legal_move(self, entity: Entity, dir:Vec2):
        # position is in the top left of every entity, so subtract 1 from the amount of times h or w of entity goes into h or w of floor
        max_x = (((self.dim.x)-entity.dim.x)/entity.dim.x)*entity.dim.x
        max_y = (((self.dim.y)-entity.dim.y)/entity.dim.y)*entity.dim.y
        prop_pos = entity.relative_position + dir
        # dir = prop_pos - entity.relative_position
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
    # load a level
    def load_level(self, level:Level):
        self.reset()
        # move the player to the spawnpoint of the level
        self.player.relative_position = self.get_pos_from_grid(level.player_spawn_grid)
        # place entities based on their emaps, and the entity instantiator attached to the key in the legend
        for key in level.emaps.keys():
            self.load_entities(level.legend[key], level.emaps[key])
    def reset(self):
        # don't remove the player
        self.entities = [self.player]
    # add entities in bulk to the grid, based on a map
    # takes an entity Class, not an initialized entity, so that it can create multiple.
    def load_entities(self, instantiator, map=[]):
        # max x and y in grid terms
        self.max_grid: Vec2 = self.get_grid_position(self.dim)
        # make sure dimensions match floor size
        if(len(map) != self.max_grid.y):
            return blogger.blog().warn("[load_entities] Map height does not match grid height")
        for row in map:
            if(len(row) != self.max_grid.x):
                return blogger.blog().warn("[load_entities] Map width does not match grid width")
        # row is y
        for row in range(0,len(map)):
            # cell is x
            for cell in range(0,len(map[row])):
                g_coord = Vec2(cell, row)
                cellval = map[row][cell]
                # if the cell = 1, then add an entity
                if(cellval == 1):
                    # instantiator is a function which returns a new, preconfigured instnace of an entity. set the position afterwards.
                    # instantiator could just be a class, or a template. either one returns an Entity
                    newe: Entity = instantiator()
                    newe.relative_position = self.get_pos_from_grid(g_coord) 
                    self.add_entity(newe)
    # count entities that contain a tag
    def count(self, tags=[]):
        count = 0
        e: Entity
        for e in self.entities:
            tagcount = 0
            for t in tags:
                if t in e.tags:
                    tagcount+=1
            if tagcount == len(tags):
                count+=1
        return count
    # dirty raycast (uses loop), 
    def raycast(self, entity:Entity, direction:Vec2, len=512):
        # generate a ray (vector line) based on the parameters
        ray = Ray(entity.relative_position, direction)
        # knowing magnitude of direction will be 1, for each increase of a value by 1, the length of ray will increase by 1
        # check for every 0.1 pixels
        for i in range(1,len*10):
            point:Vec2 = ray.get_point(i/10)
            eap = self.entity_at_point(point)
            if(eap == entity):
                continue
            if(eap):
                return eap
        return None
class Collision():
    def __init__(self, entity: Entity, pos: Vec2):
        self.entity = entity
        self.pos = pos