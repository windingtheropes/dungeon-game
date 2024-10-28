import types
import blogger
import time
import random
# generic renderer; layer 2 or layer 3; includes listener registration, render and event functions.
class Renderer():
    def __init__(self):
        self.active = True
        self.listeners = {
            "event": None,
            "render": None,
            "start": None
        }
    # register a function, fun to be triggered on events triggered by parent screens
    def _listen(self, eventName, fun):
        if eventName in self.listeners.keys() and fun != None and type(fun) == types.MethodType:
            self.listeners[eventName] = fun
        else:
            blogger.blog.warn(f"{self.__class__.__name__}) Function passed for {eventName} listener is not a function, or event does not exist.")
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
class Layer(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.screen = None
        # super(newscreen, self)._listen("render", self.render)
    # overriden render function, SAME SIGNATURE; gives a variable for a surface to render to.
    def _render(self):
        if(self.listeners["render"] != None):
            if(self.screen == None):
                blogger.blog().warn(f"{self.__class__.__name__}) Layer not initialized to a screen, not rendering.")
                return
            else:
                self.listeners["render"](self.screen)
# level 2 - layer, rendered to a screen; root _render returns a surface which is rendered to layer 1. all items must be rendered to self.surface.
class Screen(Renderer):
    def __init__(self, surface):
        Renderer.__init__(self)
        self.layers = []
        self.surface = surface;
    def add_layer(self, layer: Layer):
        if layer in self.layers:
            blogger.blog().warn(f"{self.__class__.__name__}) Layer already registered.")
        else:
            layer.screen = self.surface
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
        if(self.listeners["render"] == None):
        # if no registered listener is present, default behaviour is to render all active layers
            for l in self.layers:
                if l.active == True:
                    l._render()
        else:
            self.listeners["render"]()
        return self.surface
# level 3 - layer, renders to a screen; renders to the screen's surface.
