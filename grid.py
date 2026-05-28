class Grid:
    def __init__(self,width,height):
        self.width = width
        self.height = height

    def in_bounds(self,pos):
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def neighbors(self,pos):
        return [
            Vec2(pos.x+1,pos.y),
            Vec2(pos.x-1,pos.y),
            Vec2(pos.x,pos.y+1),
            Vec2(pos.x,pos.y-1)
        ]
 
class Vec2:
    def __init__(self,x,y):
        self.x=x
        self.y=y


    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __mul__(self,value):
        return Vec2(self.x*value,self.y*value)

    def __repr__(self):
        return f"Vec2({self.x},{self.y})"