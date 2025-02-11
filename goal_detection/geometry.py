class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def tuple(self):
        return (self.x, self.y)
    
    def shift(self, x, y):
        return Point(self.x + x, self.y + y)
    
    def __str__(self):
        return f"x: {self.x} y: {self.y}"

class Area:
    def __init__(self, up_left, bottom_right):
        self.up_left = up_left
        self.bottom_right = bottom_right
        
    def __str__(self):
        return f"point1: {self.up_left} point2: {self.bottom_right}"
    
    def size(self):
        return (self.width(), self.height())
    
    def width(self):
        return self.bottom_right.x - self.up_left.x
    
    def height(self):
        return self.bottom_right.y - self.up_left.y
    
    def extract(self, frame):
        return frame[self.up_left.y:self.bottom_right.y, self.up_left.x:self.bottom_right.x]
    
    def shift(self, x, y):
        return Area(Point(self.up_left.x + x, self.up_left.y + y), Point(self.bottom_right.x + x, self.bottom_right.y + y))
    
    def add_margin(self, margin):
        return Area(Point(self.up_left.x + margin, self.up_left.y + margin), Point(self.bottom_right.x - margin, self.bottom_right.y - margin))