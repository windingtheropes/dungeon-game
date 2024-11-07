class Vec2():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.arr = [self.x,self.y]
    def __mul__(self,b):
        return Vec2(self.x*b, self.y*b)
    def __add__(self, b):
        if(isinstance(b, Vec2)):
            return Vec2(self.x + b.x, self.y + b.y)
        else:
            raise Exception("Cannot add Vec2 and non Vec2.")
# v = Vec2(25,5)
# print((Vec2(2,2)+(v*2)).arr)