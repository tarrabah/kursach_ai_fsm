import math
import random
import time
from enum import Enum
from state_message import State_message
from path_node import Node
from player import Player
def m_round(num):
    return round(num)


class Mob_state(Enum):
    STATE_NEUTRAL, \
    STATE_WAIT, \
    STATE_PATROL, \
    STATE_MOVE_TO_SPOT, \
    STATE_LOOK_AROUND, \
    STATE_RETURN, \
    STATE_FOUND_WHILE_LOOKING_AROUND, \
    STATE_FOUND_DURING_PATROL = range(0, 8)


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
        self.chasing_point = None
        self.saved_coords = None
        self.look_around_angle = 0

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
        #print(self.state)

        if self.state == Mob_state.STATE_WAIT:
            #print("WAITING")
            if not self.time_works:
                self.time_works = True

            if self.timer > 3:
                self.timer = 0
                self.time_works = False
                self.state = Mob_state.STATE_PATROL
                #print("WAITING STOPPED")
                self.t = time.time()

        elif self.state == Mob_state.STATE_MOVE_TO_SPOT:
            if self.chasing_point.dist_to(self.x, self.y) < 0.5:
                #print('AT CHASING POINT')
                c = time.time()
                self.x = self.chasing_point.x
                self.y = self.chasing_point.y
                # print(self.id, c - self.t)
                self.t = c

                self.state = Mob_state.STATE_LOOK_AROUND
                self.look_around_angle = 0

            else:
                #print('MOVES TO CHASING POINT')
                #print("my position", self.x, self.y)
                #print("point of return:", self.chasing_point)
                self.move(lag * self.speed)
                self.update_fov_endpoints()

        elif self.state == Mob_state.STATE_LOOK_AROUND:
            if self.look_around_angle >= 2 * math.pi:
                #print('LOOKING AROUND STOPPED')
                self.state = Mob_state.STATE_RETURN
                self.angle = self.saved_coords.angle_to(self.x, self.y)
                #print("my position:",self.x, self.y)
                #print("goes to", self.saved_coords)
                #print("angle:", self.angle)
                self.look_around_angle = 0
            else:

                #print("LOOKING AROUND")
                self.angle += math.pi/50
                self.look_around_angle += math.pi/50

                spotted_enemy, enemy_coords, dist, a = self.update_fov_endpoints()
                if spotted_enemy:
                    #print("FOUND DURING LOOKING AROUND")
                    self.state = Mob_state.STATE_FOUND_WHILE_LOOKING_AROUND
                    self.angle = self.saved_coords.angle_to(self.x, self.y)
                    self.look_around_angle = 0


        elif self.state == Mob_state.STATE_RETURN:

            if self.saved_coords.dist_to(self.x, self.y) < 0.5:
                #print("HAVE RETURNED")
                c = time.time()
                self.x = round(self.x)
                self.y = round(self.y)
                #print("from:", self.chasing_point.x, self.chasing_point.y, "to", self.saved_coords.x, self.saved_coords.y)
                self.t = c

                self.state = Mob_state.STATE_PATROL
                self.angle = self.route.get_node_by_index(self.current_node + 1).angle_to(self.x, self.y)
                self.look_around_angle = 0

            else:
                #print("RETURNING")
                self.move(lag * self.speed)
                self.update_fov_endpoints()

        elif self.state == Mob_state.STATE_PATROL:
            if self.route is None:
                if self.update_fov_endpoints()[0]:
                    self.state = Mob_state.STATE_FOUND_DURING_PATROL
                else:
                    self.move(lag * self.speed)
                    self.angle += lag * 0.4
                    self.update_fov_endpoints()
            else:
                spotted_enemy, enemy_coords, dist, angle = self.update_fov_endpoints()

                if spotted_enemy:
                    if dist < 1 / 2:
                    #    print("FOUND DURING PATROL", dist)
                        self.state = Mob_state.STATE_FOUND_DURING_PATROL
                    else:
                        #print(dist)
                     #   print("SPOTTED DURING PATROL")
                        self.state = Mob_state.STATE_MOVE_TO_SPOT
                        self.chasing_point = Node(*enemy_coords)
                        #print("my position:", self.x, self.y)
                        #print("goes to:", *enemy_coords)dd


                        self.saved_coords = Node(self.x, self.y)
                        #self.x = round(self.x)
                        #self.y = round(self.y)
                    #    print("SAVED POSITION:", self.x, self.y)
                    #    print("CHASES TO:", *enemy_coords)
                        self.angle = self.chasing_point.angle_to(self.x, self.y)
                        #print("angle:", self.angle)
                else:
                    #print("DECIDES WHERE TO MOVE NEXT")
                    if self.route.get_node_by_index(self.current_node + 1).dist_to(self.x, self.y) < 0.5:
                    #    print("NEW NODE")
                        c = time.time()
                        self.x = round(self.x)
                        self.y = round(self.y)

                        self.t = c
                        self.current_node = self.route.get_next_node_index(self.current_node)
                        self.angle = self.route.get_node_by_index(self.current_node + 1).angle_to(self.x, self.y)
                    #print("PATROLS")

                    self.move(lag * self.speed)
                    self.update_fov_endpoints()

        elif self.state == Mob_state.STATE_FOUND_DURING_PATROL or self.state == Mob_state.STATE_FOUND_WHILE_LOOKING_AROUND:
            s = self.state
            #print("FOUND")
            self.field.state_observer.do_work(State_message(self.id, type(self).__name__, self.state))
            self.state = Mob_state.STATE_NEUTRAL
            #print("NEUTRAL")
            self.field.on_spotting(self.id, s)

        if self.state != prev_state:
            self.field.state_observer.do_work(State_message(self.id, type(self).__name__, self.state))

    def update_fov_endpoints(self):
        max_ray_len = 4
        ray_angle = (self.angle - self.fov / 2)
        ray_angle_change = self.fov / self.ray_amount
        ray_len_change = 0.1
        spotted_enemy = False
        enemy_coords = None, None
        dist = None
        angle = None

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
                    break
                if ray_len >= max_ray_len:
                    break

                who_there = self.field.is_anybody_there(x, y)
                if isinstance(who_there, Player):
                    #r_x, r_y = round(who_there.get_x()), round(who_there.get_y())
                    #if (r_x - who_there.get_x()) ** 2 + (r_y - who_there.get_y()) ** 2 < 0.3:
                    spotted_enemy = True
                    enemy_coords = who_there.get_x(), who_there.get_y()
                    angle = ray_angle
                    #print(ray_angle)
                    break

            self.endpoints[i][0] = x
            self.endpoints[i][1] = y

        if spotted_enemy:
            dist = math.sqrt((self.x - enemy_coords[0]) ** 2 + (self.y - enemy_coords[1]) ** 2)
            dist /= max_ray_len
        #print(dist)
        return [spotted_enemy, enemy_coords, dist, angle]


