from veclib import Vec2
import blogger

def parse_efile(path):
    f = open(path, "r") 
    content = f.read()
    f.close()
    return parse_emap(content)
    
def parse_emap(emap:str):
    grid = []
    lines = emap.split("\n")
    for l in lines:
        l = l.strip()
        row = []
        # every cell in a row is the x value
        for cell in l:
            row.append(cell)
        grid.append(row)
    return grid
class EntityMap():
    # entity template
    def __init__(self, entity, map):
        self.entity = entity
        self.map = map
# defines a level in the game (walls, entities, player spawn point)
# all positions in level are grid relative to the raw map
class Level():
    # assuming always that player is 'p'
    # takes an already parsed grid; allows for more flexibility
    def __init__(self, raw_map=[], legend={}, colours={}):
        # contains any characters
        self.raw_map = raw_map
        self.grid_dimensions = Vec2(len(self.raw_map[0]), len(self.raw_map))
        self.player_spawn_grid: Vec2 = self.find_player()
        self.legend = legend
        self.colours = colours
        # all maps in here contain only 1s and 0s (ints)
        self.emaps = {}
        self.load_emaps()
    # find the player 'p' in the map. required. then return the grid position.
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
    # generate emap (1s and 0s) from searching for 1 character in the rawmap, and converting all instances to 1 and all others to 0. returns a full grid always.
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