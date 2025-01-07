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
# find if a coordinate (cell) has openings next to it
def getOpenings(coord, level):
    openings = []
    adj = adjacent_coords(coord[0], coord[1])
    for a in adj:
        r = a[0]
        c = a[1]
        if level[r][c] == 0:
            openings.append([r,c])
    return openings

# def count_trail(point, level):
def emptycount(level):
    count = 0
    for r in level:
        for c in r:
            if c == 0:
                count+=1
    return count
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

    enrem = 3
    crem = emptycount(level)
    for r in range(1,len(level)-1):
        for c in range(1, len(level[r])-1):
            opencoords = getOpenings([r,c], level)
            if(len(opencoords) >= 1) and (level[r][c] == 0):
                if chance(crem) and enrem > 0:
                    level[r][c] = 2
                    enrem-=1
                    crem-=1
                else:
                    crem-=1
            else:
                # make sure to make powerups available in open locations
                if(chance(3) and len(getOpenings([r,c], level)) != 0):
                    level[r][c] = 3

                 
    level[5][5] = "p"
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