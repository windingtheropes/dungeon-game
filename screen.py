import types
import blogger
class Screen():
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
    # universal functions trigger registered listeners
    def _event(self, e):
        if(self.listeners["event"] != None):
            self.listeners["event"](e)
    def _render(self):
        if(self.listeners["render"] != None):
            self.listeners["render"]()

