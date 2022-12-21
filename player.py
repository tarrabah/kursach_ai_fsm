import math
from enum import Enum

def m_round(num):
    return round(num)

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
        self.speed = 4      # per
        self.state = Player_state.STATE_STATIONARY
        self.angle_table = {'w': - math.pi / 2, 'd': 0, 's': math.pi / 2, 'a': math.pi}
        self.hitbox_inc = 0.35

    def move(self, l):
        new_x, new_y = self.new_coords(l)
        if self.can_move(new_x, new_y):
            self.set_x(new_x)
            self.set_y(new_y)
        else:
            self.state = Player_state.STATE_STATIONARY
            self.set_x(round(self.x))
            self.set_y(round(self.y))
    def new_coords(self, l):
        return [self.get_x() + math.cos(self.angle) * l, self.get_y() + math.sin(self.angle) * l]
    def can_move(self, new_x, new_y):
        if (
                self.world.are_coords_safe_to_move(new_x + self.hitbox_inc, new_y + self.hitbox_inc) and
                self.world.are_coords_safe_to_move(new_x + self.hitbox_inc, new_y - self.hitbox_inc) and
                self.world.are_coords_safe_to_move(new_x - self.hitbox_inc, new_y + self.hitbox_inc) and
                self.world.are_coords_safe_to_move(new_x - self.hitbox_inc, new_y - self.hitbox_inc)
        ):
            return True
        else:
            return False
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