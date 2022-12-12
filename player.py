import math
from enum import Enum

def m_round(num):
    num = int(num + (0.5 if num > 0 else -0.5))
    return num

class Player_state(Enum):
    STATE_STATIONARY, STATE_MOVING = 0, 1


class Player:

    def __init__(self, id, world, x, y, color):
        self.id = id
        self.x = x
        self.y = y
        self.angle = 0  # math.pi / 2      # angle between x-axis and view direction
        self.move_inc = 1
        self.world = world      # class: field, means player also lives on this field
        self.color = color
        self.speed = 2      # per
        self.state = Player_state.STATE_STATIONARY
        self.angle_table = {'w': - math.pi / 2, 'd': 0, 's': math.pi / 2, 'a': math.pi}

    def move(self, l):
        new_x = self.get_x() + math.cos(self.angle) * l
        new_y = self.get_y() + math.sin(self.angle) * l

        if self.world.are_coords_safe_to_move(new_x, new_y):
            self.set_x(new_x)
            self.set_y(new_y)

    def update(self, lag):
        if self.state == Player_state.STATE_MOVING:
            self.move(self.speed * lag)

    def set_x(self, new_x):
        self.x = new_x

    def get_x(self):
        return self.x

    def set_y(self, new_y):
        self.y = new_y

    def get_y(self):
        return self.y

    def get_id(self):
        return self.id