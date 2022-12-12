class Traingle:
    def __init__(self, A, B, C):
        self.P1 = A
        self.P2 = B
        self.P3 = C

    def __str__(self):
        return self.P1.__str__() + ' ' +  self.P2.__str__() + ' ' +  self.P3.__str__()