import math
class Vec2():
    def __init__(self, x:float=0, y:float=0):
        self.x:float = float(x)
        self.y:float = float(y)
        
    def arr(self):
        return [self.x, self.y]
    # magnitude of vector; use is to be interpreted
    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)
    # return the corresponding unit vector
    def unit(self):
        return (1/self.mag()) * self
    # multiplication for int and float, scalar multiplication of vector
    def __mul__(self,b):
        return Vec2(self.x*b, self.y*b)
    def __rmul__(self,b):
        return Vec2(self.x*b, self.y*b)
    # addition of two vectors adds components
    def __add__(self, b):
        if(isinstance(b, Vec2)):
            return Vec2(self.x + b.x, self.y + b.y)
        else:
            raise Exception("Cannot add Vec2 and non Vec2.")
    def abs(self):
        return Vec2(abs(self.x), abs(self.y))
# v = Vec2(25,5)
# print((Vec2(2,2)+(v*2)).arr)

