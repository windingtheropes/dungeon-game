# from renderlib import Listener
import blogger
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
            row.append(cell)
            # try:
            #     row.append(int(cell))
            # except:
            #     blogger.blog().error("Non-int found in file.")
        grid.append(row)
    f.close()    
    return grid

class EntityMap():
    # entity class, not initialized
    def __init__(self, entity, map):
        self.entity = entity
        self.map = map
# defines a level in the game (walls, entities, player spawn point)
# all positions in level are grid relative to the raw map
class Level():
    # assuming always that player is 'p'
    def __init__(self, map_path:str="map/map.txt", legend={}):
        # contains any characters
        self.raw_map = parse_efile(map_path)
        self.grid_dimensions = Vec2(len(self.raw_map[0]), len(self.raw_map))
        self.player_spawn_grid: Vec2 = self.find_player()
        self.legend = legend
        # all maps in here contain only 1s and 0s (ints)
        self.emaps = {}
        self.load_emaps()
    # find the player 'p' in the map. required.
    def find_player(self):
        for row_i in range(len(self.raw_map)):
            row = self.raw_map[row_i]
            for cell_i in range(len(row)):
                cellval = row[cell_i]
                grid_pos = Vec2(cell_i, row_i)
                if(cellval == "p"):
                    # found the player in the map
                    return grid_pos
        return blogger.blog().error("[find_player] Player not found in file. required.")
    # generate emap (1s and 0s) from searching for 1 key in the rawmap. returns a full map regardless.
    def find_key(self, key):
        map = []
        for row_i in range(len(self.raw_map)):
            e_row = []
            row = self.raw_map[row_i]
            for cell_i in range(len(row)):
                cellval = row[cell_i]
                if(cellval == key):
                    e_row.append(1)
                else:
                    e_row.append(0)
            map.append(e_row)
        return map
    # generate emaps (0,1) from rawmap using legend
    def load_emaps(self):
        for key in self.legend.keys():
            self.emaps[key] = self.find_key(key)
