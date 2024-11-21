# from renderlib import Listener
import blogger
from veclib import Vec2
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
# parse an entity grid file into an array
def parse_efile(path):
    f = open(path, "r")
    grid = []
    # every line is a row (y value)
    for l in f:
        l = l.strip()
        row = []
        # every cell in a row is the x value
        for cell in l:
            try:
                row.append(int(cell))
            except:
                blogger.blog().error("Non-int found in file.")
        grid.append(row)
    f.close()    
    return grid

class EntityMap():
    # entity class, not initialized
    def __init__(self, entity, map):
        self.entity = entity
        self.map = map
# defines a level in the game (walls, entities, player spawn point)
class Level():
    def __init__(self):
        self.components = [] 
        self.player_spawn = Vec2(0,0)
    def add_component(self, map:EntityMap):
        if not map in self.components:
            self.components.append(map)