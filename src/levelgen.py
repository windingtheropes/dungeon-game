import random
import os
import time
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
    if r == 11:
        pass
    else:
        possibilities.append([r+1, c])

    # if not end of row, column right has an adjacent
    if c == 11:
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
def getOpeningsOnCell(coord, level, dict=[0]):
    openings = []
    adj = adjacent_coords(coord[0], coord[1])
    for a in adj:
        r = a[0]
        c = a[1]
        if level[r][c] in dict:
            openings.append([r,c])
    return openings
def getEmptyCellsOnLevel(level):
    coords = []
    for r in range(0, len(level)):
        for c in range(0,len(level[r])):
            if level[r][c] == 0:
                coords.append([r, c])
    return coords
# def count_trail(point, level):
def emptycount(level):
    count = 0
    for r in level:
        for c in r:
            if c == 0:
                count+=1
    return count

# recursively find all cells in a 'cave' by checking for openings, and the player
def getAllAccessible(coord, level, counted=[]):
    openings = getOpeningsOnCell(coord, level, [0,"p"])
    for o in openings:
        if not o in counted:
            counted.append(o)
            return getAllAccessible(o, level, counted)
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
    s = getWideSpace(openSpaces, level)
    level[s[0]][s[1]] = "p"
    for i in openSpaces:
        print(toValue(getAllAccessible(i, level), level))
    openSpaces = getEmptyCellsOnLevel(level)
    for i in range(0, random.randint(0,6)):
        s = getPlayerAccessibleSpace(level, openSpaces)
        level[s[0]][s[1]] = "3"

    openSpaces = getEmptyCellsOnLevel(level)
    for i in range(0, random.randint(2,4)):
        s = getPlayerAccessibleSpace(level, openSpaces)
        level[s[0]][s[1]] = "2"

    
    stringform = ""
    for r in range(0,len(level)):
        for c in range(0,len(level[r])):
            stringform = str(stringform) + str(level[r][c])
        if r == len(level)-1:
            continue
        stringform = stringform + "\n"
    # print(stringform)
    return stringform

# while True:
#     os.system("clear")
#     level = gen()
#     for i in level:
#         for c in i:
#             print(c, end="")
#         print("")
#     time.sleep(0.25)