import types
import blogger
import time
import random
import pygame
from vector import Vec2
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
            "render": None,
            "start": None
        }
        self.logic: Logic = None;
    # universal generic functions trigger registered listeners. this is the function that is run by the layer 1
    def _event(self, e):
        if(self.listeners["event"] != None):
            self.listeners["event"](e)
    def _render(self):
        if(self.listeners["render"] != None):
            self.listeners["render"]()
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

class Collision():
    def __init__(self, entity: Entity, pos: Vec2):
        self.entity = entity
        self.pos = pos