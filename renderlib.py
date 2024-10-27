import types
import blogger
# generic renderer; layer 2 or layer 3; includes listener registration, render and event functions.
class Renderer():
    def __init__(self):
        self.active = True
        self.listeners = {
            "event": None,
            "render": None
        }
    # register a function, fun to be triggered on events triggered by parent screens
    def _listen(self, eventName, fun):
        if eventName in self.listeners.keys() and fun != None and type(fun) == types.MethodType:
            self.listeners[eventName] = fun
        else:
            blogger.blog.warn(f"Function passed for {eventName} listener is not a function, or event does not exist.")
    # universal generic functions trigger registered listeners. this is the function that is run by the layer 1
    def _event(self, e):
        if(self.listeners["event"] != None):
            self.listeners["event"](e)
    def _render(self):
        if(self.listeners["render"] != None):
            self.listeners["render"]()
class Layer(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.screen = None
        # super(newscreen, self)._listen("render", self.render)
    # overriden render function, SAME SIGNATURE; gives a variable for a surface to render to.
    def _render(self):
        if(self.listeners["render"] != None):
            if(self.screen == None):
                blogger.blog().warn("Layer not initialized to a screen, not rendering.")
                return
            else:
                self.listeners["render"](self.screen)
# level 2 - layer, rendered to a screen; root _render returns a surface which is rendered to layer 1. all items must be rendered to self.surface.
class Screen(Renderer):
    def __init__(self, surface, default_methods=True):
        Renderer.__init__(self)
        self.layers = []
        self.surface = surface;
        if(default_methods == True):
            blogger.blog().info("Default methods are enabled. Listeners are ignored in this class.")
        self.default_methods = default_methods
    def add_layer(self, layer: Layer):
        if layer in self.layers:
            blogger.blog().warn("Layer already registered.")
        else:
            layer.screen = self.surface
            self.layers.append(layer)
        # super(newscreen, self)._listen("render", self.render)
    # methods overriden from Renderer class, MUST MATCH SIGNATURE
    def _event(self, e):
        # if default methods is true, send all events to all active layers, if default methods is false, managed by a listener
        if(self.default_methods == True):
            for l in self.layers:
                if l.active==True:
                    l._event(e)
        else:
            if(self.listeners["event"] != None):
                self.listeners["event"](e)
    def _render(self):
        # default methods will render all active layers to screen. if default methods is false, custom listener will be triggered.
        if(self.default_methods == True):
            for l in self.layers:
                if l.active == True:
                    l._render()
        else:
            if(self.listeners["render"] != None):
                self.listeners["render"]()
        return self.surface
# level 3 - layer, renders to a screen; renders to the screen's surface.
