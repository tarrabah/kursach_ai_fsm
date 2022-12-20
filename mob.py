import math
import random
import time
from enum import Enum
from state_message import State_message


def m_round(num):
    num = int(num + (0.5 if num > 0 else -0.5))
    return num


class Mob_state(Enum):
    STATE_NEUTRAL,\
    STATE_WAIT, \
    STATE_PATROLLING, \
    STATE_FOUND = range(0, 4)


class Mob:

    def __init__(self, id, field, x, y, color, route = None):
        self.id = id
        self.x = x
        self.y = y
        self.fov = math.pi / 3  # degrees
        self.field = field      # class: field, means mob lives on this field
        self.ray_amount = 20
        self.endpoints = [
            [self.x, self.y] for _ in range(self.ray_amount)
        ]
        self.speed = 3      # per s
        self.state = Mob_state.STATE_WAIT

        self.time_works = False
        self.timer = 0
        self.route = route
        self.current_node = 0
        self.color = color
        if self.route is not None:
            self.angle = self.route.get_node_by_index(self.current_node + 1).angle_to(self.x, self.y) #math.pi / 2      # angle between x-axis and view direction
        else:
            self.angle = 0

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

    def get_route(self):
        return self.route

    def move(self, l):
        new_x = self.get_x() + math.cos(self.angle) * l
        new_y = self.get_y() + math.sin(self.angle) * l

        if self.field.are_coords_safe_to_move(new_x, new_y):
            self.set_x(new_x)
            self.set_y(new_y)

    def update(self, lag):
        if self.time_works:
            self.timer += lag

        prev_state = self.state

        if self.state == Mob_state.STATE_WAIT:
            if not self.time_works:
                self.time_works = True

            if self.timer > 5:
                self.timer = 0
                self.time_works = False
                self.state = Mob_state.STATE_PATROLLING
                self.t = time.time()

        elif self.state == Mob_state.STATE_PATROLLING:
            if self.route is None:
                if self.update_fov_endpoints()[0]:
                    self.state = Mob_state.STATE_FOUND
                else:
                    self.move(lag * self.speed)
                    self.angle += lag * 0.4
                    self.update_fov_endpoints()
            else:
                if self.update_fov_endpoints()[0]:
                    self.state = Mob_state.STATE_FOUND
                else:

                    if self.route.get_node_by_index(self.current_node + 1).dist_to(self.x, self.y) < 0.3:
                        c = time.time()
                        self.x = round(self.x)
                        self.y = round(self.y)
                        #print(self.id, c - self.t)
                        self.t = c
                        self.current_node = self.route.get_next_node_index(self.current_node)

                        self.angle = self.route.get_node_by_index(self.current_node + 1).angle_to(self.x, self.y)
                    self.move(lag * self.speed)
                    self.update_fov_endpoints()

        elif self.state == Mob_state.STATE_FOUND:
            self.field.state_observer.do_work(State_message(self.id, type(self).__name__, self.state))
            self.state = Mob_state.STATE_NEUTRAL

        if self.state != prev_state:
            self.field.state_observer.do_work(State_message(self.id, type(self).__name__, self.state))

    def update_fov_endpoints(self):
        max_ray_len = 3
        ray_angle = (self.angle - self.fov / 2)
        ray_angle_change = self.fov / self.ray_amount
        ray_len_change = 0.1
        spotted_enemy = False
        enemy_coords = None, None

        for i in range(self.ray_amount):
            x, y = self.x, self.y
            ray_len = 0
            not_hit = True
            ray_angle += ray_angle_change

            while not_hit:

                ray_len += ray_len_change
                x += math.cos(ray_angle) * ray_len_change
                y += math.sin(ray_angle) * ray_len_change

                if not self.field.are_coords_safe_to_move(x, y):
                    not_hit = False
                if ray_len >= max_ray_len:
                    not_hit = False

                who_there = self.field.is_anybody_there(x, y)
                if not (who_there is None or isinstance(who_there, Mob)):
                    not_hit = False
                    spotted_enemy = True
                    enemy_coords = who_there.get_x(), who_there.get_y()

            self.endpoints[i][0] = x
            self.endpoints[i][1] = y

        return [spotted_enemy, enemy_coords]


