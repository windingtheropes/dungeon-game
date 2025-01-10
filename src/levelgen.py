import random
import os
import time
import levelslib
# levels are always 12 by 12

# calculate the 4 positions that are adjacent to a point, defined by row column coordinates
def adjacent_coords(r, c):
    possibilities = [] # r,c
    # if not the top row, a col in row above is adjacent
    if r == 0:
        pass
    else:
        possibilities.append([r-1, c])

    # if not bottom row, a col in row below is adjacent
    if r >= 11:
        pass
    else:
        possibilities.append([r+1, c])

    # if not end of row, column right has an adjacent
    if c >= 11:
        pass
    else:
        possibilities.append([r, c+1])

    # if not end of row, column left has an adjacent
    if c == 0:
        pass
    else:
        possibilities.append([r, c-1])
    return possibilities
def chance(c): # 1 in c
    if(random.randint(1,c) == random.randint(1,c)):
        return True
    return False
# find if a coordinate (cell) has openings next to it, accept dict of other values to return as well
# if walkable is true, run with the assumption that the only impassable entity is a wall
def getOpeningsOnCell(coord, level, walkable=False):
    openings = []
    adj = adjacent_coords(coord[0], coord[1])
    for a in adj:
        r = a[0]
        c = a[1]
        # print([level[r][c]])
        if walkable == False and str(level[r][c]) == "0":
            openings.append([r,c])
        elif walkable == True and str(level[r][c]) != "1":
            openings.append([r,c])
    return openings

def getEmptyCellsOnLevel(level):
    coords = []
    for r in range(0, len(level)):
        for c in range(0,len(level[r])):
            if level[r][c] == 0:
                coords.append([r, c])
    return coords

# recursively find all cells in a 'cave' by checking for openings (not walls)
def getAllAccessible(coord, level, counted=None):
    if(counted == None):
        counted = []
    openings = getOpeningsOnCell(coord, level, True)
    for o in openings:
        if not o in counted:
            counted.append(o) 
            counted = getAllAccessible(o, level, counted)
    return counted
# array of coords to array of values 
def toValue(arr, level):
    mapped = []
    for val in arr:
        mapped.append(level[val[0]][val[1]])
    return mapped

# of a list of spaces, only return one that has thresh amount of openings
def getWideSpace(spaces, level, thresh=2):
    spaces: list
    s = spaces[random.randint(0, len(spaces)-1)]
    if(len(getOpeningsOnCell(s, level)) >= thresh):
        return s
    else:
        spaces.remove(s)
        return getWideSpace(spaces, level)
    
# only return spaces that are accessible to the player
def getPlayerAccessibleSpace(level, openSpaces):
    s = getWideSpace(openSpaces, level)
    # print(toValue(getAllAccessible(s, level), level))
    if not "p" in toValue(getAllAccessible(s, level), level):
        openSpaces.remove(s)
        return getPlayerAccessibleSpace(level, openSpaces)
    else:
        return s

# generate a level, procedurally
def gen():
    level = []
    for r in range(0,12):
        c = []
        # set up borders
        for i in range(0,12):
            if i == 0 or i == 11 or r==0 or r==11:
                c.append(1)
            else:
                c.append(0)
        level.append(c)
    # work within borders
    for r in range(1,len(level)-1):
        for c in range(1, len(level[r])-1):
            adj = adjacent_coords(r, c)
            for a in adj:
                # for variety
                if(chance(5)):
                    continue
                # if the cell adjacent is a wall, very likely to build another wall next to it
                if(level[a[0]][a[1]] == 1):
                    if(chance(2)):
                        level[r][c] = 1;
                    continue
    
    openSpaces = getEmptyCellsOnLevel(level)
    player_pos = getWideSpace(openSpaces, level)
    level[player_pos[0]][player_pos[1]] = "p"    

    # if the spawn space is too small, regen
    if(len(getAllAccessible(player_pos, level)) < 20):
        return gen()

    openSpaces = getEmptyCellsOnLevel(level)
    for i in range(0, random.randint(2,4)):
        player_pos = getPlayerAccessibleSpace(level, openSpaces)
        level[player_pos[0]][player_pos[1]] = "2"

    openSpaces = getEmptyCellsOnLevel(level)
    for i in range(0, random.randint(0,6)):
        player_pos = getPlayerAccessibleSpace(level, openSpaces)
        level[player_pos[0]][player_pos[1]] = "3"
    stringform = ""
    for r in range(0,len(level)):
        for c in range(0,len(level[r])):
            stringform = str(stringform) + str(level[r][c])
        if r == len(level)-1:
            continue
        stringform = stringform + "\n"

    return stringform