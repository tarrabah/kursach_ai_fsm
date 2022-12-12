class Point_error(BaseException):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class Point:
    def __init__(self, x, y, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '(' + str(self.x) + ", " + str(self.y) + ", " + str(self.z) +')'

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            raise Point_error("unsupported operand type: " + type(other))

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Point(self.x * other, self.y * other, self.z * other)

