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
    def reset(self):
        pass
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
class Number(LogicComponent):
    def __init__(self, name:str, initial=0):
        LogicComponent.__init__(self, name)
        self.value = initial
    def inc(self, by=1):
        self.value += by 
    def dec(self, by=1):
        self.value -= by
# designed for passive access to universal game information
class Logic():
    def __init__(self):
        self.components = {}
        # Listener.__init__(self)
    def get(self, name:str) -> LogicComponent:
        return self.components[name]
    def set(self, component: LogicComponent):
        if self.components.get(component.name) != None:
            self.components[component.name] = component
        else:
            self.components.update({component.name:component})
class Tag(Enum):
    enemy="enemy"
    barrier="barrier"
