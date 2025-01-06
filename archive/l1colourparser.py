def parse(str):
    defs = {}
    colourstring = str.split(";")
    for cblock in colourstring:
        id_colour = cblock.split("(")

        id = int(id_colour[0])

        colour = id_colour[1]

        crgb = colour.split(",")
        defs[id] = (int(crgb[0]), int(crgb[1]), int(crgb[2]))
    return defs
