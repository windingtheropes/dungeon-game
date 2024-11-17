import types
import blogger
import time
import random
import pygame
from veclib import Vec2
from gamelib import Logic
# generic renderer; layer 2 or layer 3; includes listener registration, render and event functions.
class IntervalFunction:
    def __init__(self, fun, interval):
        self.fun = fun
        self.interval = interval
        self.last = 0
class Listener():
    def __init__(self):
        # listeners must be initialized as None in order to be considered valid
        self.listeners = {}
        self.interval_listeners = []
    # register a function to the listeners table
    def _listen(self, eventName, fun):
        allowed_events = self.listeners.keys()
        if eventName in allowed_events:
            if fun != None and type(fun) == types.MethodType:
                self.listeners[eventName] = fun
            else:
                blogger.blog.warn(f"{self.__class__.__name__}) Function passed for {eventName} listener is not a function.")
        else:
            blogger.blog.warn(f"{self.__class__.__name__}) Event {eventName} does not exist on {self.__class__.__name__}.")
    # interval in s
    def _listen_on_interval(self, interval, fun):
        if not interval:
            return blogger.blog.error(f"{self.__class__.__name__}) No interval passed for interval listeners.")
        if fun != None and type(fun) == types.MethodType:
            self.interval_listeners.append(IntervalFunction(fun, interval*1000))
        else:
            blogger.blog.warn(f"{self.__class__.__name__}) Function passed for interval listener is not a function.")
class Renderer(Listener):
    def __init__(self):
        Listener.__init__(self)
        self.active = True
        self.id = str(int(time.time() * random.random() * random.random()))
        self.listeners = {
            "event": None,
            "pre_render": None,
            "render": None,
            "start": None
        }
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
    def _tick(self):
        for int_fun in self.interval_listeners:
            now = pygame.time.get_ticks()
            int_fun: IntervalFunction
            if(now - int_fun.last) >= int_fun.interval:
                int_fun.last = now
                int_fun.fun()
        
# level 3 - layer, renders to a screen; renders to the screen's surface.
class Layer(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.surface:pygame.surface = None
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
        self.layers = []
        self.surface:pygame.surface = surface;
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
        if(self.listeners["event"] == None):
            # default behaviour if no event function is registered.
            for l in self.layers:
                if l.active==True:
                    l._event(e)
        else:
            self.listeners["event"](e)
    def _pre_render(self):
        # run pre render on inside layers automatically, allow for flexibility regardless whether prerender used on Screen class
        for l in self.layers:
            if l.active==True:
                l._pre_render()
        if(self.listeners["pre_render"] != None):
            self.listeners["pre_render"]()
    def _render(self):
        # render the background color as a backup, in order to prevent unexpected behaviour
        self.surface.fill((0,0,0))
        if(self.listeners["render"] == None):
        # if no registered listener is present, default behaviour is to render all active layers
            l: Layer
            for l in self.layers:
                if l.active == True:
                    # ensure that interval listeners can run at the screen level
                    l._tick()
                    l._render()
                    
        else:
            self.listeners["render"]()
        return self.surface
class Entity(Layer):
    def __init__(self):
        Layer.__init__(self)
        # tells parent to kill this item
        self._del = False
        # will collisions be calculated for this entity
        self.collidable = True
        # if solid, most items cannot pass through this entity
        self.solid = True
        # register all allowed events; includes collision
        self.listeners = {
            "event":None,
            "render":None,
            "start":None,
            "collision":None
        }
        # relative to entity floor
        self.relative_position = Vec2(0,0)
        self.dim = Vec2(32,32)
        self.facing = Vec2(0,0) # direction entity is facing
        # entity floor which this entity belongs to. Will only be given this through registration
        self.floor = None
    def _collision(self, c):
        if(self.listeners["collision"] == None):
            # default behaviour if no event function is registered.
            pass
        else:
            self.listeners["collision"](c)   
    def destroy(self):
        self._del = True
# entity floor base class; contains active entities
class EntityFloor(Layer):
    def __init__(self):
        Layer.__init__(self)
        self.entities = []
        self.pos: Vec2 = Vec2(64,64)
        # grid dimensions, as a reference unit for certain calculations
        self.gdim = 32
        self.player: Entity = None;
        self.dim: Vec2 = Vec2(384,384)
    # layer does not have built in functionality for handling layers within (layer 3.1), so it must be added like it is implemented in screens (layer 2)
    def _render(self):
        if(self.listeners["render"] == None):
        # if no registered listener is present, default behaviour is to render all active layers
            e: Entity
            for e in self.entities:
                if e.active == True:
                    rel_pos: Vec2 = e.relative_position
                    if(abs(rel_pos.x) > (self.dim.x) or abs(rel_pos.y) > (self.dim.y)) or e._del == True:
                        # remove entities far away from the dimensions of the floor, or when they're queued to be deleted
                        self.entities.remove(e)
                    else:
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
        if(not self.listeners["_pre_render"] == None):
            self.listeners["_pre_render"]()
    def add_player(self, player: Entity):
        self.player = player
        self.add_entity(player)
    def add_entity(self, entity: Entity):
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
    # **TODO** might delete later**: convert a relative position to grid coordinates, based on self.gdim (height of a grid square)
    def get_grid_position(self, relative_position:Vec2):
        # return position relative to the grid, knowing that all entities are the same size. 
        return(relative_position*(1/self.gdim)).arr()
    # convert grid position [1,0] to relative position, [1*self.gdim,0]
    def get_pos_from_grid(self, grid_position:Vec2):
        return (grid_position * self.gdim)
    # calculate collisions
    def calc_collision(self, entity: Entity, o_pos: Vec2=None):
        ### TODO CHECK FOR FOR DIRECT NEXT-TO COLLISIONS INSTEAD OF INSIDE COLLISIONS
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
            # hitbox dimension calculations
            t_pos = target.relative_position.abs()
            t_min = Vec2(t_pos.x, t_pos.y)
            t_max = Vec2(t_pos.x+target.dim.x-1, t_pos.y+target.dim.y-1)

            #     if(pos.abs().x >= t_min.x) and (pos.abs().x <= t_max.x):
            #         print("collision on x")
            #     if(pos.abs().y >= t_min.y) and (pos.abs().y <= t_max.y):
            #         print("collision on y")
            
            if(
                # entity position is greater than or equal to the minimum x; to the right
                # entity position is less than or equal to the maximum x
                ((pos.x >= t_min.x) and (pos.x <= t_max.x))
                
                and 
                # entity position is greater than or equal to the minimum y; down is positive (thanks pygame :) )
                # entity position is less than or equal to the maximum y
                ((pos.y >= t_min.y) and (pos.y <= t_max.y))
              ):
                return Collision(target, pos)
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


class Collision():
    def __init__(self, entity: Entity, pos: Vec2):
        self.entity = entity
        self.pos = pos