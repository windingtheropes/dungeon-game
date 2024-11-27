# gamelib by jack anderson
# 11/20/24
# contains game specific classes and functions
import blogger
from enum import Enum
blogger.init("log/")
from veclib import Vec2

class LogicComponent:
    def __init__(self, name:str):
        self.name = name
class PlayerInfo(LogicComponent):
    def __init__(self, name:str, max_health=3):
        LogicComponent.__init__(self, name)
        self.max_health = max_health
        self.health = self.max_health
    # increment health safely. will not go outside of [0,self.max_health]
    def inc_health(self, amt):
        if(self.health + amt) > self.max_health:
            self.health = self.max_health
        elif(self.health + amt) < 0:
            self.health = 0
        else:
            self.health += amt
# designed for passive access to universal game information
class Logic():
    def __init__(self):
        self.components = []
        # Listener.__init__(self)
    def get_component(self, name:str) -> LogicComponent:
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

class Tag(Enum):
    enemy="enemy"
    barrier="barrier"
