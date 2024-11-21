# maps
map files in this folder are to be interpreted by the Level class in gamelib. They should be of uniform dimensions (x,y), meaning there should be y rows and x cells in each row. 0s are ignored, but neccesary to denote empty space. **one** 'p' is required somewhere in each map file to define where the player will spawn. Otherwise, any character can be used (and defined in the Level legend) to spawn entities.

## example
Below is an example of a 12x12 (following game format) file defining a simple level, where 1s represent Walls, and 2s represent Enemies.
```
111111111111
1p1000000001
101000000001
101110000001
100000000001
111110000001
100000000001
102000000001
100000002000
100111000000
102000000201
111111111111
```