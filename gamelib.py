# from renderlib import Listener
import blogger
class LogicComponent:
    def __init__(self, name:str):
        self.name = name
class PlayerInfo(LogicComponent):
    def __init__(self, name:str, max_health=3):
        LogicComponent.__init__(self, name)
        self.max_health = max_health
        self.health = self.max_health
# designed for passive access to universal game information
class Logic():
    def __init__(self):
        self.components = []
        # Listener.__init__(self)
    def get_component(self, name:str):
        c: LogicComponent
        for c in self.components:
            if c.name == name:
                return c
        return None
    def add_component(self, component: LogicComponent):
        if self.get_component(component.name):
            return blogger.blog().warn(f"Component with name {component.name} already registered.")
        else:
            self.components.append(component)
