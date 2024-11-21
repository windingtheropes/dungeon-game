# veclib by Jack Anderson
# 11/20/24
# contains Vec2 (2D vector) Class and associated helper functions
import math
import blogger
import random 
class Vec2():
    def __init__(self, x:float=0, y:float=0):
        self.x:float = float(x)
        self.y:float = float(y)
    # return a readable array of x,y
    def arr(self):
        return [self.x, self.y]
    # magnitude of vector; use is to be interpreted
    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)
    # return the corresponding unit vector (length of 1)
    def unit(self):
        if(self.mag() == 0):
            blogger.blog().warn("Trying to get unit vector of vector with magnitude 0; returning 0. This should be handled in another way.")
            return Vec2(0,0)
        return (1/self.mag()) * self 
    # multiplication for int and float, scalar multiplication of vector
    def __mul__(self,b):
        return Vec2(self.x*b, self.y*b)
    def __rmul__(self,b):
        return Vec2(self.x*b, self.y*b)
    def __truediv__(self, b):
        return Vec2(self.x/b, self.y/b)
    # addition of two vectors adds components
    def __add__(self, b):
        if(isinstance(b, Vec2)):
            return Vec2(self.x + b.x, self.y + b.y)
        else:
            raise Exception("Cannot add Vec2 and non Vec2.")
    # implement subtraction like addition
    def __sub__(self, b):
        if(isinstance(b, Vec2)):
            return Vec2(self.x - b.x, self.y - b.y)
        else:
            raise Exception("Cannot sub Vec2 and non Vec2.")
    # return absolute value vactor
    def abs(self):
        return Vec2(abs(self.x), abs(self.y))
    # return vector equivalent with whole numbers (ints)
    def whole(self):
        return Vec2(int(self.x), int(self.y))
# v = Vec2(25,5)
# print((Vec2(2,2)+(v*2)).arr)
# random vector functionality
def randvec2(low: Vec2, high: Vec2):
    if not low:
        raise Exception("Low must be a valid Vec2")
    if not high:
        raise Exception("High must be a valid Vec2")
    low = low.whole()
    high = high.whole()
    return Vec2(random.randint(low.x, high.x), random.randint(low.y,high.y))

