class Point2d():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        print("x,y: ", self.x, self.y)

class Circle(Point2d):
    def __init__(self, x, y, radius):
        super().__init__(x, y)
        self.radius = radius

    def draw(self):
        print("Circle: ")
        super().draw()
        print("Radius: ", self.radius)

if __name__ == '__main__':
    point = Point2d(3, 2)
    point.draw()
    circle = Circle(3, 2, radius=5)
    circle.draw()